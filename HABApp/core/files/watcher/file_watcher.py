import asyncio
import typing
from pathlib import Path
from threading import Lock

import HABApp
from HABApp.core.wrapper import ignore_exception
from .base_watcher import BaseWatcher as __BaseWatcher

LOCK = Lock()


class AggregatingAsyncEventHandler(__BaseWatcher):
    def __init__(self, folder: Path, func: typing.Callable[[typing.List[Path]], typing.Any], file_ending: str,
                 watch_subfolders: bool = False):
        super().__init__(folder, file_ending, watch_subfolders=watch_subfolders)

        self.func = func

        self.__task: typing.Optional[asyncio.Future] = None
        self.__files: typing.Set[str] = set()

    def __execute(self):
        with LOCK:
            self.func([Path(f) for f in self.__files])
            self.__files.clear()

    @ignore_exception
    def file_changed(self, dst: str):
        # this has to be thread safe!
        with LOCK:
            self.__files.add(dst)

            # cancel already running Task
            if self.__task is not None:
                self.__task.cancel()

            # and create a new one
            self.__task = asyncio.run_coroutine_threadsafe(self.__event_waiter(), loop=HABApp.core.const.loop)

    @ignore_exception
    async def __event_waiter(self):
        try:
            # debounce time
            await asyncio.sleep(0.6)

            # trigger file event
            self.__task = None
            self.__execute()
        except asyncio.CancelledError:
            pass

    def trigger_all(self):
        files = HABApp.core.lib.list_files(self.folder, self.file_ending, self.watch_subfolders)
        self.func(files)
