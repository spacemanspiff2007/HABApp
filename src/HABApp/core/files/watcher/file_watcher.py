from asyncio import run_coroutine_threadsafe, sleep
from pathlib import Path
from time import time
from typing import Any, List, Set, Awaitable, Callable

import HABApp
from HABApp.core.wrapper import ignore_exception
from .base_watcher import EventFilterBase
from .base_watcher import FileSystemEventHandler

DEBOUNCE_TIME: float = 0.6


class AggregatingAsyncEventHandler(FileSystemEventHandler):
    def __init__(self, folder: Path, func: Callable[[List[Path]], Awaitable[Any]], filter: EventFilterBase,
                 watch_subfolders: bool = False):
        super().__init__(folder, filter, watch_subfolders=watch_subfolders)

        self.func = func

        self._files: Set[Path] = set()
        self.last_event: float = 0

    @ignore_exception
    def file_changed(self, dst: str):
        # Map from thread to async
        run_coroutine_threadsafe(self._event_waiter(Path(dst)), loop=HABApp.core.const.loop)

    @ignore_exception
    async def _event_waiter(self, dst: Path):
        self.last_event = ts = time()
        self._files.add(dst)

        # debounce time
        await sleep(DEBOUNCE_TIME)

        # check if a new event came
        if self.last_event > ts:
            return None

        # Copy Path so we're done here
        files = list(self._files)
        self._files.clear()

        # process
        await self.func(HABApp.core.lib.sort_files(files))

    async def trigger_all(self):
        files = HABApp.core.lib.list_files(self.folder, self.filter, self.watch_subfolders)
        await self.func(files)
