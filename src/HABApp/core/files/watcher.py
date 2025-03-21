import asyncio
import contextlib
import logging
import re
from asyncio import Event, Task
from collections.abc import Awaitable, Callable
from pathlib import Path
from re import Pattern
from typing import Any, Final

from typing_extensions import override
from watchfiles import Change, DefaultFilter, awatch

from HABApp.core.asyncio import create_task_from_async
from HABApp.core.wrapper import process_exception


log = logging.getLogger('HABApp.file.events')
log.setLevel(logging.INFO)


DEFAULT_FILTER = DefaultFilter()

HABAPP_DISPATCHER_PREFIX: Final = 'HABAppInternal-'


class FileWatcherDispatcherBase:

    def __init__(self, name: str, coro: Callable[[str], Awaitable[Any]],) -> None:
        self._name: Final = name
        self._coro: Final = coro

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self._name:s}>'

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return self._name

    def allow(self, change: Change | None, path: str) -> bool:
        raise NotImplementedError()

    async def dispatch(self, path: str) -> None:
        if not self.allow(None, path):
            return None

        try:
            await self._coro(path)
        except Exception as e:
            process_exception(self._coro, e, logger=log)


class FolderDispatcher(FileWatcherDispatcherBase):
    def __init__(self, name: str, coro: Callable[[str], Awaitable[Any]], folder: str) -> None:
        super().__init__(name, coro)
        self._folder: Final = folder

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FolderDispatcher):
            return False
        return self._name == other._name and self._coro is other._coro and self._folder == other._folder

    @override
    def allow(self, change: Change, path: str) -> bool:
        return path.startswith(self._folder)


class FileDispatcher(FileWatcherDispatcherBase):
    def __init__(self, name: str, coro: Callable[[str], Awaitable[Any]], file: str) -> None:
        super().__init__(name, coro)
        self._file: Final = file

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileDispatcher):
            return False
        return self._name == other._name and self._coro is other._coro and self._file == other._file

    @override
    def allow(self, change: Change, path: str) -> bool:
        return path == self._file


class HABAppFileWatcher:
    def __init__(self) -> None:
        self._dispatchers: tuple[FileWatcherDispatcherBase, ...] = ()
        self._paths: tuple[str, ...] = ()
        self._files_task: Task | None = None
        self._stop_event: Final = Event()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__:s}>'

    def cancel(self, dispatcher: FileWatcherDispatcherBase | str) -> None:
        if isinstance(dispatcher, str):
            for d in self._dispatchers:
                if d.name == dispatcher:
                    dispatcher = d
                    break
            else:
                msg = f'No dispatcher with name "{dispatcher:s}" found'
                raise ValueError(msg)

        self._dispatchers = tuple(d for d in self._dispatchers if d is not dispatcher)

    def watch_folder(self, name: str, coro: Callable[[str], Awaitable[Any]], folder: Path, *,
                     habapp_internal: bool = False) -> FolderDispatcher:
        return self._add_watcher(FolderDispatcher, name, coro, folder, habapp_internal=habapp_internal)

    def watch_file(self, name: str, coro: Callable[[str], Awaitable[Any]], file: Path, *,
                   habapp_internal: bool = False) -> FileDispatcher:
        return self._add_watcher(FileDispatcher, name, coro, file, habapp_internal=habapp_internal)

    def __notify_task(self) -> None:
        if self._files_task is None:
            self._files_task = create_task_from_async(self._watcher_task())
        else:
            self._stop_event.set()

    def _add_watcher(self, cls: type[FileDispatcher] | type[FolderDispatcher], name: str,
                     coro: Callable[[str], Awaitable[Any]], path: Path, *,
                     habapp_internal: bool = False) -> FileDispatcher | FolderDispatcher:
        d = cls(name if not habapp_internal else f'{HABAPP_DISPATCHER_PREFIX}{name}', coro, path.as_posix())
        self._add_dispatcher(d)
        self._add_path(path)
        return d

    def _add_dispatcher(self, dispatcher: FileWatcherDispatcherBase) -> None:
        name = dispatcher.name.lower()
        for d in self._dispatchers:
            if d.name.lower() != name or d == dispatcher:
                continue
            msg = f'Dispatcher with name "{dispatcher.name:s}" already exists'
            raise ValueError(msg)

        self._dispatchers += (dispatcher, )
        log.debug(f'Added dispatcher {dispatcher.name:s}')
        self.__notify_task()

    def _add_path(self, path: Path) -> None:
        if path.as_posix() in self._paths:
            return None

        if not path.is_dir() and not path.is_file():
            msg = f'Path {path} does not exist'
            raise FileNotFoundError(msg)

        self._paths += (path.as_posix(), )
        log.debug(f'Watching {path}')

        self.__notify_task()

    def _watch_filter(self, change: Change | None, path: str, *,
                      dispatchers: list[FileWatcherDispatcherBase] | None = None) -> bool:
        if not DEFAULT_FILTER(change, path):
            return False

        if dispatchers is not None:
            return any(dispatcher.allow(change, path) for dispatcher in dispatchers)

        process = any(dispatcher.allow(change, path) for dispatcher in self._dispatchers)
        log.debug(f'{change.name:s} {path:s}{" (ignored)" if not process else ""}')
        return process

    async def _watcher_task(self) -> None:
        delay = 1
        while self._dispatchers:
            await asyncio.sleep(1)

            try:
                self._stop_event.clear()
                log.debug('Starting file watcher')
                async for changes in awatch(*self._paths, watch_filter=self._watch_filter, stop_event=self._stop_event):
                    file_names = [Path(p).as_posix() for _, p in changes]
                    for dispatcher in self._dispatchers:
                        for path in file_names:
                            await dispatcher.dispatch(path)

                log.debug('File watcher stopped')
            except Exception as e:  # noqa: PERF203
                process_exception(self._watcher_task, e, logger=log)
                delay *= 2
                await asyncio.sleep(delay)

        log.debug('File watcher shutdown')

    async def shutdown(self) -> None:
        self._dispatchers = ()
        self._stop_event.set()
        if self._files_task is None:
            return None

        task = self._files_task
        self._files_task = None

        try:
            return await asyncio.wait_for(task, 2)
        except asyncio.TimeoutError:
            pass

        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
        return None

    async def load_files(self, dispatcher_name_include: Pattern | str | None = None,
                         dispatcher_name_exclude: Pattern | str | None = None,
                         *,
                         exclude_habapp_config: bool = True) -> None:

        if isinstance(dispatcher_name_include, str):
            dispatcher_name_include = re.compile(dispatcher_name_include)
        if isinstance(dispatcher_name_exclude, str):
            dispatcher_name_exclude = re.compile(dispatcher_name_exclude)

        dispatchers = []
        for d in self._dispatchers:
            name = d.name

            if name.startswith(HABAPP_DISPATCHER_PREFIX):
                if exclude_habapp_config:
                    continue
                name = name.removeprefix(HABAPP_DISPATCHER_PREFIX)

            if exclude_habapp_config and d.name.lower().startswith(HABAPP_DISPATCHER_PREFIX):
                continue
            if dispatcher_name_include is not None and not dispatcher_name_include.search(name):
                continue
            if dispatcher_name_exclude is not None and dispatcher_name_exclude.search(name):
                continue
            dispatchers.append(d)

        if not dispatchers:
            msg = 'No dispatchers selected!'
            raise ValueError(msg)

        files: list[str] = []
        for path_str in self._paths:
            if not self._watch_filter(None, path_str, dispatchers=dispatchers):
                continue
            path = Path(path_str)

            if path.is_file():  # noqa: PTH113
                files.append(path.as_posix())
                continue

            if path.is_dir():
                for obj in path.glob('**/*'):
                    obj_str = obj.as_posix()
                    if self._watch_filter(None, obj_str, dispatchers=dispatchers):
                        files.append(obj_str)

        for file in sorted(files):
            for dispatcher in self._dispatchers:
                if dispatcher.allow(None, file):
                    await dispatcher.dispatch(file)
