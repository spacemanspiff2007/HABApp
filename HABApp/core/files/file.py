from __future__ import annotations

import logging
import typing
import HABApp
from pathlib import Path
from HABApp.core.wrapper import ignore_exception
from HABApp.core.events.habapp_events import RequestFileLoadEvent, RequestFileUnloadEvent
from .file_props import FileProperties, get_props
from HABApp.core.const.topics import FILES as T_FILES

log = logging.getLogger('HABApp.files')


class CircularReferenceError(Exception):
    pass


class HABAppFile:

    @classmethod
    def from_path(cls, name: str, path: Path) -> HABAppFile:
        with path.open('r', encoding='utf-8') as f:
            txt = f.read(10 * 1024)
        return cls(name, path, get_props(txt))

    def __init__(self, name: str, path: Path, properties: FileProperties):
        self.name: str = name
        self.path: Path = path
        self.properties: FileProperties = properties

        # file checks
        self.is_checked = False
        self.is_valid = False

        # file loaded
        self.is_loaded = False
        self.is_failed = False

    def _check_refs(self, stack, prop: str):
        c: typing.List[str] = getattr(self.properties, prop)
        for f in c:
            _stack = stack + (f, )
            if f in stack:
                log.error(f'Circular reference: {" -> ".join(_stack)}')
                raise CircularReferenceError(" -> ".join(_stack))

            next_file = ALL.get(f)
            if next_file is not None:
                next_file._check_refs(_stack, prop)

    @ignore_exception
    def check_properties(self):
        self.is_checked = True

        # check dependencies
        mis = set(filter(lambda x: x not in ALL, self.properties.depends_on))
        if mis:
            one = len(mis) == 1
            msg = f'File {self.path} depends on file{"" if one else "s"} that ' \
                  f'do{"es" if one else ""}n\'t exist: {", ".join(mis)}'
            log.error(msg)
            raise FileNotFoundError(msg)

        # check reload
        mis = set(filter(lambda x: x not in ALL, self.properties.reloads_on))
        if mis:
            one = len(mis) == 1
            log.warning(f'File {self.path} reloads on file{"" if one else "s"} that '
                        f'do{"es" if one else ""}n\'t exist: {", ".join(mis)}')

        # check for circular references
        self._check_refs((self.name, ), 'depends_on')
        self._check_refs((self.name, ), 'reloads_on')

        self.is_valid = True

    def can_be_loaded(self) -> bool:
        if not self.is_valid:
            return False

        for name in self.properties.depends_on:
            if not ALL.get(name, False).is_loaded:
                return False
        return True

    def load(self):
        self.is_loaded = False

        HABApp.core.EventBus.post_event(
            T_FILES, RequestFileLoadEvent(self.name)
        )

    def unload(self):
        HABApp.core.EventBus.post_event(
            T_FILES, RequestFileUnloadEvent(self.name)
        )

    def load_ok(self):
        self.is_loaded = True

    def load_failed(self):
        self.is_failed = True


from .all import ALL    # noqa F401
