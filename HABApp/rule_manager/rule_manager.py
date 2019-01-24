import asyncio
import datetime
import logging
import math
import threading
import time
import traceback
import typing
from pathlib import Path

from watchdog.observers import Observer

import HABApp
from HABApp.util import PrintException, SimpleFileWatcher
from .rule_file import RuleFile

log = logging.getLogger('HABApp.Rules')


class RuleManager:

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
                    HABApp.core.Workers.submit(self.add_file, f)

        HABApp.core.Workers.submit(delayed_load)

        # folder watcher
        self.__folder_watcher = Observer()
        self.__folder_watcher.schedule(
            SimpleFileWatcher(self.__file_event, file_ending='.py', ),
            path=str(self.runtime.config.directories.rules),
            recursive=True
        )
        self.__folder_watcher.start()

        # proper shutdown
        self.runtime.shutdown.register_func(self.__folder_watcher.stop)
        self.runtime.shutdown.register_func(self.__folder_watcher.join)

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


    def __file_event(self, path):
        assert isinstance(path, Path), type(path)
        if path.is_file():
            HABApp.core.Workers.submit(self.add_file, path)


    def add_file(self, path : Path):
        log.debug( f'Loading file: {path}')

        file = None
        try:
            # serialize loading
            with self.__lock:

                # unload old callbacks
                path_str = str(path)
                if path_str in self.files:
                    for rule in self.files[path_str].iterrules():   # type: HABApp.Rule
                        rule._cleanup()

                file = RuleFile(self, path)
                self.files[path_str] = file
                file.load()
        except Exception:
            log.error(f"Could not load {path}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'File {path} successfully loaded!')

        # Do simple checks which prevent errors
        file.check_all_rules()
