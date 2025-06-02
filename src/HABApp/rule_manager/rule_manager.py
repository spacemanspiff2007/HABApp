import logging
import re
import typing
from asyncio import sleep
from pathlib import Path

import HABApp
import HABApp.__cmd_args__ as cmd_args
from HABApp.core import shutdown
from HABApp.core.connections import Connections
from HABApp.core.files.errors import AlreadyHandledFileError
from HABApp.core.internals import uses_item_registry
from HABApp.core.internals.proxy import uses_file_manager
from HABApp.core.internals.wrapped_function import wrap_func
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import log_exception
from HABApp.rule_manager.rule_file import RuleFile


log = logging.getLogger('HABApp.Rules')

item_registry = uses_item_registry()
file_manager = uses_file_manager()


class RuleManager:

    def __init__(self, parent) -> None:
        assert isinstance(parent, HABApp.runtime.Runtime)
        self.runtime = parent

        self.files: typing.Dict[str, RuleFile] = {}

    async def setup(self):

        # shutdown
        shutdown.register(self.shutdown, msg='Cancel rule schedulers')

        if cmd_args.DO_BENCH:
            from HABApp.rule_manager.benchmark import BenchFile
            self.files['bench'] = file = BenchFile(self)
            ok = await wrap_func(file.load).async_run()
            if not ok:
                log.error('Failed to load Benchmark!')
                shutdown.request()
                return None
            await file.check_all_rules()
            return None

        path = HABApp.CONFIG.directories.rules
        prefix = 'rules/'

        file_manager.add_handler(
            self.__class__.__name__, log, prefix=prefix,
            on_load=self.request_file_load, on_unload=self.request_file_unload
        )
        file_manager.add_folder(
            prefix, path, priority=0, pattern=re.compile(r'.py$', re.IGNORECASE), name='rules-python'
        )

        # Initial loading of rules
        HABApp.core.internals.wrap_func(self.load_rules_on_startup, logger=log).run()

    async def load_rules_on_startup(self):

        if HABApp.CONFIG.openhab.general.wait_for_openhab:
            c = Connections.get('openhab')
            while not (c.is_shutdown or c.is_disabled or c.is_online):
                await sleep(1)
        else:
            await sleep(1)

        # if we want to shut down we don't load the rules
        if shutdown.is_requested():
            return None

        # trigger event for every file
        await file_manager.get_file_watcher().load_files(dispatcher_name_include=r'^rules.*$')
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
            msg = f'No Rule with name "{rule_name}" found!'
            raise KeyError(msg)
        return found if len(found) > 1 else found[0]

    async def request_file_unload(self, name: str, path: Path) -> None:
        path_str = str(path)

        # Only unload already loaded files
        if path_str not in self.files:
            log_warning(log, f'Rule file {path} is not yet loaded and therefore can not be unloaded')
            return None

        log.debug(f'Removing file: {name}')
        rule = self.files.pop(path_str)

        await rule.unload()
        return None

    async def request_file_load(self, name: str, path: Path) -> None:
        path_str = str(path)

        # if we want to shut down we don't load the rules
        if shutdown.is_requested():
            log.debug(f'Skip load of {name:s} because of shutdown')
            return None

        # Only load existing files
        if not path.is_file():
            log_warning(log, f'Rule file {name} ({path}) does not exist and can not be loaded!')
            return None

        log.debug(f'Loading file: {name}')
        self.files[path_str] = rule_file = RuleFile(self, name, path)

        ok = await rule_file.load()
        if not ok:
            self.files.pop(path_str)
            log.warning(f'Failed to load {path_str}!')
            raise AlreadyHandledFileError()

        log.debug(f'File {name} successfully loaded!')

        # Do simple checks which prevent errors
        await rule_file.check_all_rules()
        return None

    async def shutdown(self) -> None:
        for f in self.files.values():
            await f.unload()
