from __future__ import annotations

import logging
import re
from asyncio import Lock, sleep
from typing import TYPE_CHECKING, Any, Final

import HABApp.__cmd_args__ as cmd_args
from HABApp.core.connections import ConnectionManager
from HABApp.core.files.errors import AlreadyHandledFileError
from HABApp.core.internals import ExecutorFactory
from HABApp.core.logger import log_warning
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.core.wrapper import log_exception
from HABApp.rule_manager.rule_file import RuleFile


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator
    from pathlib import Path

    from HABApp.config import ApplicationConfig
    from HABApp.core.files import FileManager
    from HABApp.core.shutdown import ShutdownInfo


log = logging.getLogger('HABApp.Rules')


class RuleManager:

    def __init__(self, shutdown: ShutdownInfo, file_manager: FileManager, config: ApplicationConfig) -> None:

        self._shutdown: Final = shutdown
        self._file_manager: Final = file_manager
        self._config: Final = config

        self._files: Final[dict[str, RuleFile]] = {}
        self._lock: Final = Lock()

    async def setup(self) -> None:
        if cmd_args.DO_BENCH:
            from HABApp.rule_manager.benchmark import BenchFile

            executor_factory = await HABAPP_PROVIDER.get(ExecutorFactory)

            async with self._lock:
                self._files['bench'] = file = BenchFile(self)
                ok = await executor_factory.create(file.load).execute()
                if not ok:
                    log.error('Failed to load Benchmark!')
                    self._shutdown.request_showdown()
                    return None
                await file.check_all_rules()
                return None

        path = self._config.directories.rules
        prefix = 'rules/'

        self._file_manager.add_handler(
            self.__class__.__name__, log, prefix=prefix,
            on_load=self.request_file_load, on_unload=self.request_file_unload
        )
        self._file_manager.add_folder(
            prefix, path, priority=0, pattern=re.compile(r'.py$', re.IGNORECASE), name='rules-python'
        )
        return None

    async def load_rules_on_startup(self) -> None:

        connections = await HABAPP_PROVIDER.get(ConnectionManager)

        if self._config.openhab.general.wait_for_openhab:
            c = connections.get('openhab')
            while not (c.is_shutdown or c.is_disabled or c.is_online or self._shutdown.is_requested()):
                await sleep(1)
        else:
            await sleep(1)

        # if we want to shut down we don't load the rules
        if self._shutdown.is_requested():
            return None

        # trigger event for every file
        await self._file_manager.get_file_watcher().load_files(dispatcher_name_include=r'^rules.*$')
        return None

    @log_exception
    def get_rule(self, rule_name):
        found = []
        for file in self._files.values():
            if rule_name is None:
                for rule in file.rules.values():
                    found.append(rule)
            elif rule_name in file.rules:
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

        async with self._lock:
            # Only unload already loaded files
            if path_str not in self._files:
                log_warning(log, f'Rule file {path} is not yet loaded and therefore can not be unloaded')
                return None

            log.debug(f'Removing file: {name}')
            rule = self._files.pop(path_str)

            await rule.unload()
            return None

    async def request_file_load(self, name: str, path: Path) -> None:
        path_str = str(path)

        # if we want to shut down we don't load the rules
        if self._shutdown.is_requested():
            log.debug(f'Skip load of {name:s} because of shutdown')
            return None

        # Only load existing files
        if not path.is_file():
            log_warning(log, f'Rule file {name} ({path}) does not exist and can not be loaded!')
            return None

        async with self._lock:
            log.debug(f'Loading file: {name}')
            self._files[path_str] = rule_file = RuleFile(self, name, path)

            ok = await rule_file.load()
            if not ok:
                self._files.pop(path_str)
                log.warning(f'Failed to load {path_str}!')
                raise AlreadyHandledFileError()

            log.debug(f'File {name} successfully loaded!')

            # Do simple checks which prevent errors
            await rule_file.check_all_rules()
            return None

    async def unload_rules(self) -> None:
        async with self._lock:
            while self._files:
                _, f = self._files.popitem()
                await f.unload()


@HABAPP_PROVIDER.register
async def _provide_manger(shutdown: ShutdownInfo, file_manager: FileManager,
                          config: ApplicationConfig) -> AsyncGenerator[RuleManager, Any]:

    obj = RuleManager(shutdown, file_manager, config)
    await obj.setup()
    yield obj
    await obj.unload_rules()
