from __future__ import annotations

import logging
import typing
from pathlib import Path
from typing import Callable, Awaitable, Any

from HABApp.core.files.errors import CircularReferenceError, DependencyDoesNotExistError, AlreadyHandledFileError
from HABApp.core.files.file.properties import FileProperties
from HABApp.core.files.manager.files import FILES, file_state_changed
from HABApp.core.wrapper import process_exception
from . import FileState

log = logging.getLogger('HABApp.files')


class HABAppFile:
    LOGGER: logging.Logger
    LOAD_FUNC: Callable[[str, Path], Awaitable[Any]]
    UNLOAD_FUNC: Callable[[str, Path], Awaitable[Any]]

    def __init__(self, name: str, path: Path, properties: FileProperties):
        self.name: str = name
        self.path: Path = path

        self.state: FileState = FileState.PENDING
        self.properties: FileProperties = properties
        log.debug(f'{self.name} added')

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name} state: {self.state}>'

    def set_state(self, new_state: FileState):
        if self.state is new_state:
            return None

        self.state = new_state
        log.debug(f'{self.name} changed to {self.state}')
        file_state_changed(self)

    def _check_circ_refs(self, stack, prop: str):
        c: typing.List[str] = getattr(self.properties, prop)
        for f in c:
            _stack = stack + (f, )
            if f in stack:
                raise CircularReferenceError(_stack)

            next_file = FILES.get(f)
            if next_file is not None:
                next_file._check_circ_refs(_stack, prop)

    def _check_properties(self):
        # check dependencies
        mis = set(filter(lambda x: x not in FILES, self.properties.depends_on))
        if mis:
            one = len(mis) == 1
            msg = f'File {self.path} depends on file{"" if one else "s"} that ' \
                  f'do{"es" if one else ""}n\'t exist: {", ".join(sorted(mis))}'

            raise DependencyDoesNotExistError(msg)

        # check reload
        mis = set(filter(lambda x: x not in FILES, self.properties.reloads_on))
        if mis:
            one = len(mis) == 1
            log.warning(f'File {self.path} reloads on file{"" if one else "s"} that '
                        f'do{"es" if one else ""}n\'t exist: {", ".join(sorted(mis))}')

    def check_properties(self, log_msg: bool = False):
        if self.state is not FileState.PENDING and self.state is not FileState.DEPENDENCIES_ERROR:
            return None

        try:
            self._check_properties()
        except DependencyDoesNotExistError as e:
            if log_msg:
                log.error(e.msg)
            return self.set_state(FileState.DEPENDENCIES_ERROR)

        try:
            # check for circular references
            self._check_circ_refs((self.name, ), 'depends_on')
            self._check_circ_refs((self.name, ), 'reloads_on')
        except CircularReferenceError as e:
            log.error(f'Circular reference: {" -> ".join(e.stack)}')
            return self.set_state(FileState.DEPENDENCIES_ERROR)

        # Check if we can already load it
        self.set_state(FileState.DEPENDENCIES_OK if not self.properties.depends_on else FileState.DEPENDENCIES_MISSING)

    def check_dependencies(self):
        if self.state is not FileState.DEPENDENCIES_MISSING:
            return None

        for name in self.properties.depends_on:
            f = FILES.get(name, None)
            if f is None:
                return None
            if f.state is not FileState.LOADED:
                return None

        self.set_state(FileState.DEPENDENCIES_OK)
        return None

    async def load(self):
        assert self.state is FileState.DEPENDENCIES_OK, self.state

        try:
            await self.__class__.LOAD_FUNC(self.name, self.path)
        except Exception as e:
            if not isinstance(e, AlreadyHandledFileError):
                process_exception(self.__class__.LOAD_FUNC, e, logger=self.LOGGER)
            self.set_state(FileState.FAILED)
            return None

        self.set_state(FileState.LOADED)
        return None

    async def unload(self):
        try:
            await self.__class__.UNLOAD_FUNC(self.name, self.path)
        except Exception as e:
            if not isinstance(e, AlreadyHandledFileError):
                process_exception(self.__class__.UNLOAD_FUNC, e, logger=self.LOGGER)
            self.set_state(FileState.FAILED)
            return None

        self.set_state(FileState.REMOVED)
        return None

    def file_changed(self, file: HABAppFile):
        name = file.name
        if name in self.properties.reloads_on:
            self.set_state(FileState.PENDING)
