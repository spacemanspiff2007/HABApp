import asyncio
from pathlib import Path
from time import time
from typing import Any, Callable, List, Set

import HABApp
from HABApp.core.wrapper import ignore_exception
from .base_watcher import BaseWatcher as __BaseWatcher


class AggregatingAsyncEventHandler(__BaseWatcher):
    def __init__(self, folder: Path, func: Callable[[List[Path]], Any], file_ending: str,
                 watch_subfolders: bool = False):
        super().__init__(folder, file_ending, watch_subfolders=watch_subfolders)

        self.func = func

        self._files: Set[Path] = set()
        self.last_event: float = 0

    @ignore_exception
    def file_changed(self, dst: str):
        # Map from thread to async
        asyncio.run_coroutine_threadsafe(self._event_waiter(Path(dst)), loop=HABApp.core.const.loop)

    @ignore_exception
    async def _event_waiter(self, dst: Path):
        self.last_event = ts = time()
        self._files.add(dst)

        # debounce time
        await asyncio.sleep(0.6)
        
        # check if a new event came
        if self.last_event > ts:
            return None

        # Build Path objs
        files = list(self._files)
        self._files.clear()
        self.func(files)

    def trigger_all(self):
        files = HABApp.core.lib.list_files(self.folder, self.file_ending, self.watch_subfolders)
        self.func(files)
