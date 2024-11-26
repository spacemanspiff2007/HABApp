from asyncio import run_coroutine_threadsafe, sleep
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import HABApp
from HABApp.core.wrapper import ignore_exception

from .base_watcher import EventFilterBase, FileSystemEventHandler


DEBOUNCE_TIME: float = 0.6


class AggregatingAsyncEventHandler(FileSystemEventHandler):
    def __init__(self, folder: Path, func: Callable[[list[Path]], Awaitable[Any]], filter: EventFilterBase,
                 watch_subfolders: bool = False) -> None:
        super().__init__(folder, filter, watch_subfolders=watch_subfolders)

        self.func = func

        self._files: set[Path] = set()
        self._event_obj: object = object()

    @ignore_exception
    def file_changed(self, dst: str) -> None:
        # Map from thread to async
        run_coroutine_threadsafe(self._event_waiter(Path(dst)), loop=HABApp.core.const.loop)

    @ignore_exception
    async def _event_waiter(self, dst: Path):
        self._event_obj = event_obj = object()
        self._files.add(dst)

        # debounce time
        await sleep(DEBOUNCE_TIME)

        # check if a new event came
        if self._event_obj is not event_obj:
            return None

        # Copy Path so we're done here
        files = list(self._files)
        self._files.clear()

        # process
        await self.func(HABApp.core.lib.sort_files(files))

    async def trigger_all(self) -> None:
        files = HABApp.core.lib.list_files(self.folder, self.filter, self.watch_subfolders)
        await self.func(files)
