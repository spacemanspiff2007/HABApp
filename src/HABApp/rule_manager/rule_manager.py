import logging
import threading
import typing
from asyncio import sleep
from pathlib import Path

import HABApp
import HABApp.__cmd_args__ as cmd_args
from HABApp.core.files.errors import AlreadyHandledFileError
from HABApp.core.files.file import HABAppFile
from HABApp.core.files.folders import add_folder as add_habapp_folder
from HABApp.core.files.watcher import AggregatingAsyncEventHandler
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import log_exception
from HABApp.runtime import shutdown
from .rule_file import RuleFile

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

        self.watcher: typing.Optional[AggregatingAsyncEventHandler] = None

    async def setup(self):

        # shutdown
        shutdown.register_func(self.shutdown, msg='Cancel rule schedulers')

        if cmd_args.DO_BENCH:
            from HABApp.rule_manager.benchmark import BenchFile
            self.files['bench'] = file = BenchFile(self)
            ok = await HABApp.core.const.loop.run_in_executor(HABApp.core.WrappedFunction._WORKERS, file.load)
            if not ok:
                log.error('Failed to load Benchmark!')
                HABApp.runtime.shutdown.request_shutdown()
                return None
            file.check_all_rules()
            return

        class HABAppRuleFile(HABAppFile):
            LOGGER = log
            LOAD_FUNC = self.request_file_load
            UNLOAD_FUNC = self.request_file_unload

        path = HABApp.CONFIG.directories.rules
        folder = add_habapp_folder('rules/', path, 0)
        folder.add_file_type(HABAppRuleFile)
        self.watcher = folder.add_watch('.py', True)

        # Initial loading of rules
        HABApp.core.WrappedFunction(self.load_rules_on_startup, logger=log).run()

    async def load_rules_on_startup(self):

        if HABApp.CONFIG.openhab.connection.host and HABApp.CONFIG.openhab.general.wait_for_openhab:
            items_found = False
            while not items_found:
                await sleep(3)
                for item in HABApp.core.Items.get_all_items():
                    if isinstance(item, HABApp.openhab.items.OpenhabItem):
                        items_found = True
                        break

                # stop waiting if we want to shut down
                if HABApp.runtime.shutdown.requested:
                    return None
            await sleep(2.2)
        else:
            await sleep(5.2)

        # trigger event for every file
        await self.watcher.trigger_all()
        return None

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

    async def request_file_unload(self, name: str, path: Path, request_lock=True):
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

            log.debug(f'Removing file: {name}')
            with self.__files_lock:
                rule = self.files.pop(path_str)

            await HABApp.core.const.loop.run_in_executor(HABApp.core.WrappedFunction._WORKERS, rule.unload)
        finally:
            if request_lock:
                self.__load_lock.release()

    async def request_file_load(self, name: str, path: Path):
        path_str = str(path)

        # Only load existing files
        if not path.is_file():
            log_warning(log, f'Rule file {name} ({path}) does not exist and can not be loaded!')
            return None

        with self.__load_lock:
            # Unload if we have already loaded
            with self.__files_lock:
                already_loaded = path_str in self.files
            if already_loaded:
                await self.request_file_unload(name, path, request_lock=False)

            log.debug(f'Loading file: {name}')
            with self.__files_lock:
                self.files[path_str] = file = RuleFile(self, name, path)

            ok = await HABApp.core.const.loop.run_in_executor(HABApp.core.WrappedFunction._WORKERS, file.load)
            if not ok:
                self.files.pop(path_str)
                log.warning(f'Failed to load {path_str}!')
                raise AlreadyHandledFileError()

        log.debug(f'File {name} successfully loaded!')

        # Do simple checks which prevent errors
        file.check_all_rules()

    def shutdown(self):
        for f in self.files.values():
            for rule in f.rules.values():
                rule._unload()
