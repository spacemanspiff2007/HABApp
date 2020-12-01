import asyncio
import datetime
import logging
import math
import threading
import time
import typing

from pytz import utc

import HABApp
from pathlib import Path
from HABApp.core.files import file_load_failed, file_load_ok
from HABApp.core.files.watcher import AggregatingAsyncEventHandler
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import log_exception
from .rule_file import RuleFile

log = logging.getLogger('HABApp.Rules')


LOAD_DELAY = 1


async def set_load_ok(name: str):
    await asyncio.sleep(LOAD_DELAY)
    file_load_ok(name)


async def set_load_failed(name: str):
    await asyncio.sleep(LOAD_DELAY)
    file_load_failed(name)


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

        self.watcher: typing.Optional[AggregatingAsyncEventHandler] = None

    def setup(self):

        # Add event bus listener
        HABApp.core.files.add_event_bus_listener('rule', self.request_file_load, self.request_file_unload, log)

        # Folder watcher
        self.watcher = HABApp.core.files.watch_folder(HABApp.CONFIG.directories.rules, '.py', True)

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

                # stop waiting if we want to shut down
                if self.runtime.shutdown.requested:
                    return None
            time.sleep(2.2)
        else:
            time.sleep(5.2)

        # trigger event for every file
        self.watcher.trigger_all()
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
    def request_file_unload(self, name: str, path: Path, request_lock=True):
        path_str = str(path)

        try:
            if request_lock:
                self.__load_lock.acquire()

            # Only unload already loaded files
            with self.__files_lock:
                already_loaded = path_str in self.files
            if not already_loaded:
                log_warning(log, f'Rule file {path} is not yet loaded and therefore can not be unloaded')
                return None

            log.debug(f'Removing file: {path}')
            with self.__files_lock:
                rule = self.files.pop(path_str)
            rule.unload()
        except Exception as e:
            err = HABApp.core.logger.HABAppError(log)
            err.add(f"Could not remove {path}!")
            err.add_exception(e, True)
            err.dump()
            return None
        finally:
            if request_lock:
                self.__load_lock.release()

    @log_exception
    def request_file_load(self, name: str, path: Path):
        path_str = str(path)

        # Only load existing files
        if not path.is_file():
            log_warning(log, f'Rule file {path} does not exist and can not be loaded!')
            return None

        with self.__load_lock:
            # Unload if we have already loaded
            with self.__files_lock:
                already_loaded = path_str in self.files
            if already_loaded:
                self.request_file_unload(name, path, request_lock=False)

            log.debug(f'Loading file: {path}')
            with self.__files_lock:
                self.files[path_str] = file = RuleFile(self, path)

            if not file.load():
                # If the load has failed we remove it again.
                # Unloading is handled directly in the load function
                self.files.pop(path_str)
                log.warning(f'Failed to load {path_str}!')

                # signal that we have loaded the file but with a small delay
                asyncio.run_coroutine_threadsafe(set_load_failed(name), HABApp.core.const.loop)
                return None

        log.debug(f'File {path_str} successfully loaded!')

        # signal that we have loaded the file but with a small delay
        asyncio.run_coroutine_threadsafe(set_load_ok(name), HABApp.core.const.loop)

        # Do simple checks which prevent errors
        file.check_all_rules()
