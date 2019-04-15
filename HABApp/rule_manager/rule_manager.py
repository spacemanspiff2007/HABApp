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
from HABApp.runtime import FileEventTarget

log = logging.getLogger('HABApp.Rules')


class RuleManager(FileEventTarget):

    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime = parent

        self.files: typing.Dict[str, RuleFile] = {}

        # serialize loading
        self.__lock = threading.Lock()

        # if we load immediately we don't have the items from openhab in itemcache
        def delayed_load():
            time.sleep(5)
            for f in self.runtime.config.directories.rules.glob('**/*.py'):
                if f.name.endswith('.py'):
                    time.sleep(0.5)
                    HABApp.core.WrappedFunction(self.add_file, logger=log).run(f)

        HABApp.core.WrappedFunction(delayed_load, logger=log, warn_too_long=False).run()

        # folder watcher
        self.runtime.folder_watcher.watch_folder(
            folder=self.runtime.config.directories.rules,
            file_ending='.py',
            event_target=self,
            worker_factory=lambda x : HABApp.core.WrappedFunction(x, logger=log).run,
            watch_subfolders=True
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

    @PrintException
    def get_rule(self, rule_name):
        found = []
        for file in self.files.values():
            if rule_name in file.rules:
                found.append(file.rules[rule_name])
        if not found:
            raise KeyError(f'No Rule with name "{rule_name}" found!')
        return found if len(found) > 1 else found[0]

    @PrintException
    def reload_file(self, path: Path):
        self.remove_file(path)
        self.add_file(path)

    @PrintException
    def remove_file(self, path: Path):
        try:
            with self.__lock:
                path_str = str(path)
                log.debug(f'Removing file: {path}')
                if path_str in self.files:
                    self.files.pop(path_str).unload()
        except Exception:
            log.error(f"Could not remove {path}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

    @PrintException
    def add_file(self, path : Path):

        try:
            # serialize loading
            with self.__lock:
                path_str = str(path)

                log.debug(f'Loading file: {path}')
                self.files[path_str] = file = RuleFile(self, path)
                file.load()
        except Exception:
            log.error(f"Could not (fully) load {path}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'File {path_str} successfully loaded!')

        # Do simple checks which prevent errors
        file.check_all_rules()
