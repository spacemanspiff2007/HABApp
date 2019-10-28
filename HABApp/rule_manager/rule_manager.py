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

RULES_TOPIC = 'HABApp.Rules'


class RuleManager(FileEventTarget):

    def __init__(self, parent):
        assert isinstance(parent, HABApp.runtime.Runtime)
        self.runtime = parent

        self.files: typing.Dict[str, RuleFile] = {}

        # serialize loading
        self.__file_load_lock = threading.Lock()
        self.__rulefiles_lock = threading.Lock()

        # Processing
        self.__process_last_sec = 60


        # Listener to add rules
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                RULES_TOPIC,
                HABApp.core.WrappedFunction(self.request_file_load),
                HABApp.core.events.events.RequestFileLoadEvent
            )
        )

        # listener to remove rules
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                RULES_TOPIC,
                HABApp.core.WrappedFunction(self.request_file_unload),
                HABApp.core.events.events.RequestFileUnloadEvent
            )
        )

        # folder watcher
        self.runtime.folder_watcher.watch_folder(
            folder=self.runtime.config.directories.rules, file_ending='.py', event_target=self, watch_subfolders=True
        )

        # Initial loading of rules
        HABApp.core.WrappedFunction(self.load_rules_on_startup, logger=log, warn_too_long=False).run()

    def load_rules_on_startup(self):

        if self.runtime.config.openhab.connection.host and self.runtime.config.openhab.general.wait_for_openhab:
            items_found = False
            while not items_found:
                time.sleep(3)
                for item in HABApp.core.Items.get_all_items():
                    if isinstance(item, (HABApp.openhab.items.NumberItem, HABApp.openhab.items.ContactItem,
                                         HABApp.openhab.items.SwitchItem, HABApp.openhab.items.RollershutterItem,
                                         HABApp.openhab.items.DimmerItem, HABApp.openhab.items.ColorItem)):
                        items_found = True
                        break
            time.sleep(0.2)
        else:
            time.sleep(5.2)

        # trigger event for every file
        for f in self.runtime.config.directories.rules.glob('**/*.py'):
            if f.name.endswith('.py'):
                time.sleep(1)
                filename = str(f.relative_to(self.runtime.config.directories.rules))
                HABApp.core.EventBus.post_event(
                    RULES_TOPIC, HABApp.core.events.events.RequestFileLoadEvent(filename)
                )
        return None

    @PrintException
    async def process_scheduled_events(self):

        while not self.runtime.shutdown.requested:

            now = datetime.datetime.now()

            # process only once per second
            if now.second == self.__process_last_sec:
                await asyncio.sleep(0.1)
                continue
            self.__process_last_sec = now.second

            with self.__rulefiles_lock:
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
            if rule_name is None:
                for rule in file.rules.values():
                    found.append(rule)
            else:
                if rule_name in file.rules:
                    found.append(file.rules[rule_name])

        # if we want all return them
        if rule_name is None:
            return found

        # if we want a special one throw error
        if not found:
            raise KeyError(f'No Rule with name "{rule_name}" found!')
        return found if len(found) > 1 else found[0]

    @PrintException
    def on_file_changed(self, path: Path):
        HABApp.core.EventBus.post_event(
            RULES_TOPIC, HABApp.core.events.events.RequestFileUnloadEvent(path.name)
        )
        time.sleep(0.1)
        HABApp.core.EventBus.post_event(
            RULES_TOPIC, HABApp.core.events.events.RequestFileLoadEvent(path.name)
        )

    @PrintException
    def on_file_removed(self, path: Path):
        HABApp.core.EventBus.post_event(
            RULES_TOPIC, HABApp.core.events.events.RequestFileUnloadEvent(path.name)
        )

    @PrintException
    def on_file_added(self, path : Path):
        time.sleep(0.1)
        HABApp.core.EventBus.post_event(
            RULES_TOPIC, HABApp.core.events.events.RequestFileLoadEvent(path.name)
        )

    @PrintException
    def request_file_unload(self, event: HABApp.core.events.events.RequestFileUnloadEvent):

        path = self.runtime.config.directories.rules / event.filename
        path_str = str(path)

        # Only unload already loaded files
        if path_str not in self.files:
            log.warning(f'Rule file {path} is not yet loaded and therefore can not be unloaded')
            return None

        try:
            with self.__file_load_lock:
                log.debug(f'Removing file: {path}')
                if path_str in self.files:
                    with self.__rulefiles_lock:
                        rule = self.files.pop(path_str)
                    rule.unload()
        except Exception:
            log.error(f"Could not remove {path}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

    @PrintException
    def request_file_load(self, event: HABApp.core.events.events.RequestFileLoadEvent):

        path = self.runtime.config.directories.rules / event.filename

        # Only load existing files
        if not path.is_file():
            log.warning(f'Rule file {path} does not exist and can not be loaded!')
            return None

        try:
            # serialize loading
            with self.__file_load_lock:
                path_str = str(path)

                log.debug(f'Loading file: {path}')
                with self.__rulefiles_lock:
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
