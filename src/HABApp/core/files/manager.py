from __future__ import annotations

import asyncio
import logging
from asyncio import sleep
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING, Final

from pydantic import ValidationError

import HABApp
from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.files.file import HABAppFile
from HABApp.core.files.file_properties import get_file_properties
from HABApp.core.files.name_builder import FileNameBuilder
from HABApp.core.lib import SingleTask


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from re import Pattern

    from HABApp.core.events.habapp_events import RequestFileLoadEvent, RequestFileUnloadEvent
    from HABApp.core.files.watcher import HABAppFileWatcher


log = logging.getLogger('HABApp.files')


class FileTypeHandler:
    def __init__(self, name: str, logger: logging.Logger, *,
                 prefix: str, pattern: Pattern | None = None,
                 on_load: Callable[[str, Path], Awaitable[None]],
                 on_unload: Callable[[str, Path], Awaitable[None]]) -> None:
        self.name: Final = name
        self.logger: Final = logger

        self.prefix: Final = prefix
        self.pattern: Final = pattern

        self.on_load: Final = on_load
        self.on_unload: Final = on_unload

    def matches(self, name: str) -> bool:
        if not name.startswith(self.prefix):
            return False

        if (p := self.pattern) is not None and not p.search(name):  # noqa: SIM103
            return False

        return True

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.name:s}>'


class FileManager:
    def __init__(self, watcher: HABAppFileWatcher | None) -> None:
        self._lock = asyncio.Lock()
        self._files: Final[dict[str, HABAppFile]] = {}

        self._files_request_load: Final[set[str]] = set()
        self._files_request_unload: Final[set[str]] = set()

        self._file_names: Final = FileNameBuilder()
        self._file_handlers: tuple[FileTypeHandler, ...] = ()

        self._task: Final = SingleTask(self._load_file_task, name='file load worker')
        self._watcher: Final = watcher

        self._event_received: bool = False

    def add_folder(self, prefix: str, folder: Path, *,
                   name: str, priority: int, pattern: Pattern | None = None) -> None:
        self._file_names.add_folder(prefix, folder, priority=priority, pattern=pattern)
        if self._watcher is not None:
            self._watcher.watch_folder(name, self.file_watcher_event, folder)

    def get_file_watcher(self) -> HABAppFileWatcher:
        if self._watcher is None:
            raise ValueError()
        return self._watcher

    def get_folders(self):  # noqa: ANN201
        return self._file_names.get_folders()

    def add_handler(self, name: str, logger: logging.Logger, *,
                   prefix: str, pattern: Pattern | None = None,
                   on_load: Callable[[str, Path], Awaitable[None]],
                   on_unload: Callable[[str, Path], Awaitable[None]]) -> None:

        for h in self._file_handlers:
            if h.name == name:
                msg = f'Handler {name:s} already exists!'
                raise ValueError(msg)
            if h.prefix == prefix and h.pattern == pattern:
                msg = f'Handler with prefix {prefix:s} and pattern {pattern} already exists!'
                raise ValueError(msg)

        new = FileTypeHandler(name, logger, prefix=prefix, pattern=pattern, on_load=on_load, on_unload=on_unload)
        self._file_handlers += (new, )
        log.debug(f'Added handler {new.name}')

    def get_file(self, name: str) -> HABAppFile | None:
        return self._files.get(name)

    def file_state_changed(self, file: HABAppFile, new_state: str) -> None:
        log.debug(f'{file.name} changed to {new_state:s}')
        for f in self._files.values():
            f.file_state_changed(file, self)

    def _get_file_handler(self, name: str) -> FileTypeHandler:
        handlers = [h for h in self._file_handlers if h.matches(name)]
        if not handlers:
            msg = f'No handler matched for {name:s}'
            raise ValueError(msg)

        if len(handlers) > 1:
            msg = f'Multiple handlers matches for {name:s}: {", ".join(str(h) for h in handlers)}'
            raise ValueError(msg)

        return handlers[0]

    async def _do_file_load(self, name: str) -> None:
        if not (file := self.get_file(name)):
            return None
        await file.load(self._get_file_handler(name), manager=self)

    async def _do_file_unload(self, name: str) -> None:
        if not (file := self.get_file(name)):
            return None
        await file.unload(self._get_file_handler(name), manager=self)

        if file.can_be_removed():
            self._files.pop(name)

    async def _load_file_task(self) -> None:
        try:
            task_sleep = 0.4
            task_alive = 15

            task_shutdown = False
            last_process = monotonic()

            while True:
                await sleep(0)

                # wait to aggregate changes
                while True:
                    async with self._lock:
                        if not self._event_received:
                            break
                        self._event_received = False

                    await sleep(task_sleep)

                async with self._lock:
                    # we first try to unload all files
                    if self._files_request_unload:
                        # unload order is reverse of load order, since we unload unconditionally we can
                        unload_name = next(self._file_names.get_names(self._files_request_unload, reverse=True))
                        self._files_request_unload.remove(unload_name)
                        await self._do_file_unload(unload_name)
                        last_process = monotonic()
                        continue

                    # then we add all the files we want to load
                    if self._files_request_load:
                        load_name = next(self._file_names.get_names(self._files_request_load))
                        if (existing := self.get_file(load_name)) and existing.can_be_unloaded():
                            self._files_request_unload.add(load_name)
                            continue
                        self._files_request_load.remove(load_name)
                        self._files[load_name] = self.__create_file(load_name)
                        last_process = monotonic()
                        continue

                    # Once we cleared all the queues the proper processing starts:
                    # check files for dependencies etc.
                    for file in self._files.values():
                        file.check_properties(self, log, log_msg=task_shutdown)
                        file.check_dependencies(self)

                    # unload pending files
                    if unload_pending := [f.name for f in self._files.values() if f.state_unload_pending()]:
                        name = next(self._file_names.get_names(unload_pending, reverse=True))
                        await self._do_file_unload(name)
                        last_process = monotonic()
                        continue

                    # load files
                    if can_be_loaded := [f.name for f in self._files.values() if f.can_be_loaded()]:
                        name = next(self._file_names.get_names(can_be_loaded))
                        await self._do_file_load(name)
                        last_process = monotonic()
                        continue

                if task_shutdown:
                    break
                await sleep(0.1)
                task_shutdown = monotonic() - last_process > task_alive

        except Exception as e:
            HABApp.core.wrapper.process_exception(self._task.name, e, logger=log)
        log.debug('Worker done!')

    def __accept_event(self, event: RequestFileLoadEvent | RequestFileUnloadEvent) -> bool:
        if not self._file_names.is_accepted_name(event.name):
            HABApp.core.logger.log_error(log, f'Ignoring {event.__class__.__name__} for invalid name "{event.name}"')
            return False
        return True

    def __create_file(self, name: str) -> HABAppFile:
        path = self._file_names.create_path(name)
        text = path.read_text()
        checksum = HABAppFile.create_checksum(text)
        try:
            properties = get_file_properties(text)
        except ValidationError as e:
            properties = None
            HABApp.core.logger.log_error(log, str(e))

        habapp_file = HABAppFile(name, path, checksum, properties)
        log.debug(f'{habapp_file.name} created in state {habapp_file._state:s}')
        return habapp_file

    async def event_load(self, event: RequestFileLoadEvent) -> None:
        if not self.__accept_event(event):
            return None

        self._task.start_if_not_running()

        async with self._lock:
            self._event_received = True
            self._files_request_load.add(event.name)

    async def event_unload(self, event: RequestFileUnloadEvent) -> None:
        if not self.__accept_event(event):
            return None

        self._task.start_if_not_running()

        async with self._lock:
            self._event_received = True
            self._files_request_unload.add(event.name)

    async def file_watcher_event(self, path: str) -> None:
        if not self._file_names.is_accepted_path(path):
            return None

        obj = Path(path)
        name = self._file_names.create_name(path)

        if obj.is_dir():
            return None

        if not obj.is_file():
            HABApp.core.EventBus.post_event(TOPIC_FILES, HABApp.core.events.habapp_events.RequestFileUnloadEvent(name))
            return None

        if existing := self.get_file(name):
            checksum = HABAppFile.create_checksum(obj.read_text())
            if existing.checksum == checksum:
                log.debug(f'Skip file system event because file {name:s} did not change')
                return None

        HABApp.core.EventBus.post_event(TOPIC_FILES, HABApp.core.events.habapp_events.RequestFileLoadEvent(name))
        return None

    def setup(self) -> None:
        HABApp.core.EventBus.add_listener(
            HABApp.core.internals.EventBusListener(
                TOPIC_FILES, HABApp.core.internals.wrap_func(self.event_load),
                HABApp.core.events.EventFilter(HABApp.core.events.habapp_events.RequestFileLoadEvent)
            )
        )

        HABApp.core.EventBus.add_listener(
            HABApp.core.internals.EventBusListener(
                TOPIC_FILES, HABApp.core.internals.wrap_func(self.event_unload),
                HABApp.core.events.EventFilter(HABApp.core.events.habapp_events.RequestFileUnloadEvent)
            )
        )
