import asyncio
import datetime
import logging
import traceback
import typing
from pathlib import Path

from watchdog.observers import Observer

import HABApp
from HABApp.util import SimpleFileWatcher, PrintException
from .rule_file import RuleFile

log = logging.getLogger('HABApp.Rules')


class RuleManager:

    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime = parent

        self.files = {} # type: typing.Dict[str, RuleFile]

        for f in self.runtime.config.directories['rules'].iterdir():
            if f.name.endswith('.py'):
                self.runtime.workers.submit(self.add_file, f)

        # folder watcher
        self.__folder_watcher = Observer()
        self.__folder_watcher.schedule(SimpleFileWatcher(self.__file_event, file_ending='.py'), str(self.runtime.config.directories['rules']))
        self.__folder_watcher.start()

        #proper shutdown
        self.runtime.shutdown.register_func(self.__folder_watcher.stop)
        self.runtime.shutdown.register_func(self.__folder_watcher.join)

        self.__process_last_sec = 60

        #asyncio.gather(self.process_scheduled_events())
        #asyncio.ensure_future(self.process_scheduled_events())


    @PrintException
    async def process_scheduled_events(self):

        while not self.runtime.shutdown.requested:

            now = datetime.datetime.now()

            # process only once per sec
            if now.second == self.__process_last_sec:
                continue
            self.__process_last_sec = now.second

            for file in self.files.values():
                assert isinstance(file, RuleFile), type(file)
                for rule in file.iterrules():
                    rule._process_sheduled_events(now)

            await asyncio.sleep(0.2)


    @PrintException
    def get_async(self):
        return asyncio.gather(self.process_scheduled_events())


    def get_rule(self, rule_name) -> typing.Union[list, HABApp.Rule]:
        found = []
        for file in self.files.values():
            if rule_name in file.rules:
                found.append(file.rules[rule_name])
        if not found:
            raise KeyError(f'No Rule with name "{rule_name}" found!')
        return found if len(found) > 1 else found[0]


    def __file_event(self, path):
        self.runtime.workers.submit(self.add_file, path)


    def add_file(self, path : Path):
        log.debug( f'Loading file: {path}')

        try:
            # unload old callbacks
            path_str = str(path)
            if path_str in self.files:
                for rule in self.files[path_str].iterrules():   # type: HABApp.Rule
                    rule._cleanup()

            file = RuleFile(self, path)
            file.load()
            self.files[path_str] = file
        except Exception:
            log.error(f"Could not load {path}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)

        log.debug(f'File {path} successfully loaded!')
