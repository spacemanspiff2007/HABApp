from __future__ import annotations

from enum import Enum, auto
from hashlib import blake2b
from typing import TYPE_CHECKING, Final

from HABApp.core.files.errors import AlreadyHandledFileError, CircularReferenceError, DependencyDoesNotExistError
from HABApp.core.files.file_properties import FileProperties
from HABApp.core.wrapper import process_exception


if TYPE_CHECKING:
    import logging
    from pathlib import Path

    from HABApp.core.files.manager import FileManager, FileTypeHandler


class FileState(Enum):
    LOADED = auto()
    FAILED = auto()

    DEPENDENCIES_OK = auto()
    DEPENDENCIES_MISSING = auto()
    DEPENDENCIES_ERROR = auto()

    PROPERTIES_INVALID = auto()  # Properties could not be parsed

    # if the file should be automatically unloaded
    UNLOAD_PENDING = auto()

    # initial and last state
    PENDING = auto()
    REMOVED = auto()

    def __str__(self) -> str:
        return str(self.name)


class HABAppFile:

    @staticmethod
    def create_checksum(text: str) -> bytes:
        b = blake2b()
        b.update(text.encode())
        return b.digest()

    def __init__(self, name: str, path: Path, checksum: bytes, properties: FileProperties | None) -> None:
        self.name: Final = name
        self.path: Final = path
        self.checksum: Final = checksum
        self.properties: Final = properties if properties is not None else FileProperties()
        self._state: FileState = FileState.PENDING if properties is not None else FileState.PROPERTIES_INVALID

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.name} state: {self._state}>'

    def set_state(self, new_state: FileState, manager: FileManager) -> None:
        if self._state is new_state:
            return None

        self._state = new_state
        manager.file_state_changed(self, str(new_state))

    def _check_circ_refs(self, stack: tuple[str, ...], prop: str, manager: FileManager) -> None:
        c: list[str] = getattr(self.properties, prop)
        for f in c:
            _stack = stack + (f, )
            if f in stack:
                raise CircularReferenceError(_stack)

            next_file = manager.get_file(f)
            if next_file is not None:
                next_file._check_circ_refs(_stack, prop, manager)

    def _check_properties(self, manager: FileManager, log: logging.Logger) -> None:
        # check dependencies
        missing = {name for name in self.properties.depends_on if manager.get_file(name) is None}
        if missing:
            one = len(missing) == 1
            msg = (f'File {self.path} depends on file{"" if one else "s"} that '
                   f'do{"es" if one else ""}n\'t exist: {", ".join(sorted(missing))}')
            raise DependencyDoesNotExistError(msg)

        # check reload
        missing = {name for name in self.properties.reloads_on if manager.get_file(name) is None}
        if missing:
            one = len(missing) == 1
            log.warning(f'File {self.path} reloads on file{"" if one else "s"} that '
                        f'do{"es" if one else ""}n\'t exist: {", ".join(sorted(missing))}')

    def check_properties(self, manager: FileManager, log: logging.Logger, *, log_msg: bool = False) -> None:
        if self._state is not FileState.PENDING and self._state is not FileState.DEPENDENCIES_ERROR:
            return None

        try:
            self._check_properties(manager, log)
        except DependencyDoesNotExistError as e:
            if log_msg:
                log.error(e.msg)
            return self.set_state(FileState.DEPENDENCIES_ERROR, manager)

        try:
            # check for circular references
            self._check_circ_refs((self.name, ), 'depends_on', manager)
            self._check_circ_refs((self.name, ), 'reloads_on', manager)
        except CircularReferenceError as e:
            log.error(f'Circular reference: {" -> ".join(e.stack)}')
            return self.set_state(FileState.DEPENDENCIES_ERROR, manager)

        # Check if we can already load it
        new_state = FileState.DEPENDENCIES_OK if not self.properties.depends_on else FileState.DEPENDENCIES_MISSING
        self.set_state(new_state, manager)
        return None

    def check_dependencies(self, manager: FileManager) -> None:
        if self._state is not FileState.DEPENDENCIES_MISSING:
            return None

        for name in self.properties.depends_on:
            if (file := manager.get_file(name)) is None:
                return None
            if file._state is not FileState.LOADED:
                return None

        self.set_state(FileState.DEPENDENCIES_OK, manager)
        return None

    def can_be_loaded(self) -> bool:
        return self._state is FileState.DEPENDENCIES_OK

    def state_unload_pending(self) -> bool:
        return self._state is FileState.UNLOAD_PENDING

    def can_be_removed(self) -> bool:
        return self._state is FileState.REMOVED

    def can_be_unloaded(self) -> bool:
        # If we are loaded we are either FAILED or LOADED.
        # With failed the handler will have already unloaded the file
        return self._state is FileState.LOADED

    async def load(self, handler: FileTypeHandler, manager: FileManager) -> None:
        if not self.can_be_loaded():
            msg = f'File {self.name} can not be loaded because current state is {self._state}!'
            raise ValueError(msg)

        try:
            await handler.on_load(self.name, self.path)
        except Exception as e:
            if not isinstance(e, AlreadyHandledFileError):
                process_exception(handler.on_load, e, logger=handler.logger)
            self.set_state(FileState.FAILED, manager)
            return None

        self.set_state(FileState.LOADED, manager)
        return None

    async def unload(self, handler: FileTypeHandler, manager: FileManager) -> None:
        try:
            await handler.on_unload(self.name, self.path)
        except Exception as e:
            if not isinstance(e, AlreadyHandledFileError):
                process_exception(handler.on_unload, e, logger=handler.logger)

            if self._state is FileState.UNLOAD_PENDING:
                self.set_state(FileState.PENDING, manager)
            else:
                self.set_state(FileState.FAILED, manager)
            return None

        if self._state is FileState.UNLOAD_PENDING:
            self.set_state(FileState.PENDING, manager)
        else:
            self.set_state(FileState.REMOVED, manager)
        return None

    def file_state_changed(self, file: HABAppFile, manager: FileManager) -> None:
        name = file.name
        if name in self.properties.reloads_on:
            if self.can_be_unloaded():
                self.set_state(FileState.UNLOAD_PENDING, manager)
            else:
                self.set_state(FileState.PENDING, manager)
