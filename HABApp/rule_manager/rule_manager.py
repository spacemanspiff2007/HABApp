import asyncio
import datetime
import logging
import math
import threading
import time
import traceback
import typing
from pathlib import Path

import HABApp
from HABApp.util import PrintException
from .rule_file import RuleFile

log = logging.getLogger('HABApp.Rules')


class RuleManager:

    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime = parent

        self.files: typing.Dict[str, RuleFile] = {}

        # serialize loading
        self.__lock = threading.Lock()

        # wrapper to load files, do not reuse an instantiated WrappedFunction because it will throw errors
        # in the traceback module
        def load_file_wrapper(path):
            return HABApp.core.WrappedFunction(self.add_file, logger=log).submit(path)

        # if we load immediately we don't have the items from openhab in itemcache
        def delayed_load():
            time.sleep(5)
            for f in self.runtime.config.directories.rules.glob('**/*.py'):
                if f.name.endswith('.py'):
                    time.sleep(0.5)
                    load_file_wrapper( f)

        HABApp.core.WrappedFunction(delayed_load, logger=log, warn_too_long=False).submit()

        # folder watcher
        self.runtime.file_watcher.watch_folder(
            folder=self.runtime.config.directories.rules,
            file_ending='.py',
            callback=load_file_wrapper,
            recursive=True
        )

        self.__process_last_sec = 60

    @PrintException
    async def process_scheduled_events(self):

        while not self.runtime.shutdown.requested:

            now = datetime.datetime.now()

            # process only once per second
            if now.second == self.__process_last_sec:
                await asyncio.sleep(0.1)
                continue
            self.__process_last_sec = now.second

            for file in self.files.values():
                assert isinstance(file, RuleFile), type(file)
                for rule in file.iterrules():
                    rule._process_events(now)

            # sleep longer, try to sleep until the next full second
            end = datetime.datetime.now()
            if end.second == self.__process_last_sec:
                frac, whole = math.modf(time.time())
                sleep_time = 1 - frac + 0.005   # prevent rounding error and add a little bit of security
                await asyncio.sleep( sleep_time)


    @PrintException
    def get_async(self):
        return asyncio.gather(self.process_scheduled_events())


    def get_rule(self, rule_name):
        found = []
        for file in self.files.values():
            if rule_name in file.rules:
                found.append(file.rules[rule_name])
        if not found:
            raise KeyError(f'No Rule with name "{rule_name}" found!')
        return found if len(found) > 1 else found[0]


    def add_file(self, path : Path):

        file_exists = path.is_file()

        file = None
        try:
            # serialize loading
            with self.__lock:
                path_str = str(path)

                log.debug(f'{"Loading" if file_exists else "Removing"} file: {path}')

                # unload old callbacks
                if path_str in self.files:
                    self.files.pop(path_str).unload()

                # If the file doesn't exist we can stop after unloading it
                if not file_exists:
                    return None

                file = RuleFile(self, path)
                self.files[path_str] = file
                file.load()
        except Exception:
            log.error(f"Could not (fully) load {path}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'File {path_str} successfully loaded!')

        # Do simple checks which prevent errors
        file.check_all_rules()
