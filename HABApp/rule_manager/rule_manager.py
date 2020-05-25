import asyncio
import datetime
import logging
import math
import threading
import time
import traceback
import typing

from pytz import utc

import HABApp
from HABApp.core.wrapper import log_exception
from .rule_file import RuleFile
from HABApp.core.const.topics import RULES as TOPIC_RULES

log = logging.getLogger('HABApp.Rules')



class RuleManager:

    def __init__(self, parent):
        assert isinstance(parent, HABApp.runtime.Runtime)
        self.runtime = parent

        self.files: typing.Dict[str, RuleFile] = {}

        # serialize loading
        self.__load_lock = threading.Lock()
        self.__files_lock = threading.Lock()

        # Processing
        self.__process_last_sec = 60


        # Listener to add rules
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                TOPIC_RULES,
                HABApp.core.WrappedFunction(self.request_file_load),
                HABApp.core.events.habapp_events.RequestFileLoadEvent
            )
        )

        # listener to remove rules
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                TOPIC_RULES,
                HABApp.core.WrappedFunction(self.request_file_unload),
                HABApp.core.events.habapp_events.RequestFileUnloadEvent
            )
        )

        # Initial loading of rules
        HABApp.core.WrappedFunction(self.load_rules_on_startup, logger=log, warn_too_long=False).run()

    def load_rules_on_startup(self):

        if HABApp.CONFIG.openhab.connection.host and HABApp.CONFIG.openhab.general.wait_for_openhab:
            items_found = False
            while not items_found:
                time.sleep(3)
                for item in HABApp.core.Items.get_all_items():
                    if isinstance(item, HABApp.openhab.items.OpenhabItem):
                        items_found = True
                        break
            time.sleep(0.2)
        else:
            time.sleep(5.2)

        # trigger event for every file
        w = self.runtime.folder_watcher.get_handler(HABApp.CONFIG.directories.rules)
        w.trigger_load_for_all_files(delay=1)
        return None

    @log_exception
    async def process_scheduled_events(self):

        while not self.runtime.shutdown.requested:

            now = datetime.datetime.now(tz=utc)

            # process only once per second
            if now.second == self.__process_last_sec:
                await asyncio.sleep(0.1)
                continue

            # remember sec
            self.__process_last_sec = now.second

            with self.__files_lock:
                for file in self.files.values():
                    assert isinstance(file, RuleFile), type(file)
                    for rule in file.rules.values():
                        rule._process_events(now)

            # sleep longer, try to sleep until the next full second
            end = datetime.datetime.now(tz=utc)
            if end.second == self.__process_last_sec:
                frac, whole = math.modf(time.time())
                sleep_time = 1 - frac + 0.005   # prevent rounding error and add a little bit of security
                await asyncio.sleep(sleep_time)


    @log_exception
    def get_async(self):
        return asyncio.gather(self.process_scheduled_events())

    @log_exception
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


    @log_exception
    def request_file_unload(self, event: HABApp.core.events.habapp_events.RequestFileUnloadEvent, request_lock=True):
        path = event.get_path(HABApp.CONFIG.directories.rules)
        path_str = str(path)

        try:
            if request_lock:
                self.__load_lock.acquire()

            # Only unload already loaded files
            with self.__files_lock:
                already_loaded = path_str in self.files
            if not already_loaded:
                log.warning(f'Rule file {path} is not yet loaded and therefore can not be unloaded')
                return None

            log.debug(f'Removing file: {path}')
            with self.__files_lock:
                rule = self.files.pop(path_str)
            rule.unload()
        except Exception:
            log.error(f"Could not remove {path}!")
            for line in traceback.format_exc().splitlines():
                log.error(line)
            return None
        finally:
            if request_lock:
                self.__load_lock.release()

    @log_exception
    def request_file_load(self, event: HABApp.core.events.habapp_events.RequestFileLoadEvent):

        path = event.get_path(HABApp.CONFIG.directories.rules)
        path_str = str(path)

        # Only load existing files
        if not path.is_file():
            log.warning(f'Rule file {path} does not exist and can not be loaded!')
            return None

        with self.__load_lock:
            # Unload if we have already loaded
            with self.__files_lock:
                already_loaded = path_str in self.files
            if already_loaded:
                self.request_file_unload(event, request_lock=False)

            log.debug(f'Loading file: {path}')
            with self.__files_lock:
                self.files[path_str] = file = RuleFile(self, path)

            if not file.load():
                # If the load has failed we remove it again.
                # Unloading is handled directly in the load function
                self.files.pop(path_str)
                log.warning(f'Failed to load {path_str}!')
                return None

        log.debug(f'File {path_str} successfully loaded!')

        # Do simple checks which prevent errors
        file.check_all_rules()
