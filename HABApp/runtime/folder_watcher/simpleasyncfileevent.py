import asyncio
import typing
from pathlib import Path
from threading import Lock

from watchdog.events import FileSystemEventHandler

import HABApp
from HABApp.core.wrapper import ignore_exception

LOCK = Lock()


class SimpleAsyncEventHandler(FileSystemEventHandler):
    def __init__(self, target_func: typing.Callable[[Path], typing.Any], file_ending: str, worker_factory=None):
        self.__target_func = target_func

        assert isinstance(file_ending, str), type(file_ending)
        self.file_ending = file_ending

        # Possibility to use a wrapper to load files
        # do not reuse an instantiated WrappedFunction because it will throw errors in the traceback module
        self.__worker_factory = worker_factory

        # Pending events
        self.__tasks: typing.Dict[str, asyncio.Future] = {}

    def __execute(self, dst: str):
        if self.__worker_factory is None:
            return self.__target_func(Path(dst))
        return self.__worker_factory(self.__target_func)(Path(dst))

    def dispatch(self, event):

        # we don't process directory events
        if event.is_directory:
            return None

        src = event.src_path
        if src.endswith(self.file_ending):
            self.process_dst(src)

        # moved events have a dst, so we process it, too
        if hasattr(event, 'dest_path'):
            dst = event.dest_path
            if dst.endswith(self.file_ending):
                self.process_dst(dst)
        return None

    @ignore_exception
    def process_dst(self, dst: str):
        # this has to be thread safe!
        with LOCK:
            try:
                # cancel already running Task
                self.__tasks[dst].cancel()
            except KeyError:
                pass
            # and create a new one
            self.__tasks[dst] = asyncio.run_coroutine_threadsafe(self.event_waiter(dst), loop=HABApp.core.const.loop)

    @ignore_exception
    async def event_waiter(self, dst: str):
        try:
            # debounce time
            await asyncio.sleep(0.4)

            # remove debounce task for target file
            with LOCK:
                _ = self.__tasks.pop(dst, None)

            # trigger file event
            self.__execute(dst)
        except asyncio.CancelledError:
            pass
