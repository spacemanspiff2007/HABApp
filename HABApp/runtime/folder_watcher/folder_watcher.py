import pathlib
import typing

from watchdog.observers import Observer

from .habappfileevent import FileEventToHABAppEvent
from .simpleasyncfileevent import SimpleAsyncEventHandler


class FolderWatcher:
    def __init__(self):

        self.__observer = Observer()
        self.__handlers: typing.Dict[str, typing.Union[SimpleAsyncEventHandler, FileEventToHABAppEvent]] = {}
        self.__watches = {}
        self.__started = False

    def start(self, shutdown_helper):
        from ..shutdown_helper import ShutdownHelper
        assert isinstance(shutdown_helper, ShutdownHelper)

        # we shall only start once!
        assert self.__started is False
        self.__started = True

        # start watching the folders
        self.__observer.start()

        # register for proper shutdown
        shutdown_helper.register_func(self.__observer.stop)
        shutdown_helper.register_func(self.__observer.join, last=True)
        return None

    def watch_folder(self, folder: pathlib.Path, file_ending: str, target_func,
                     watch_subfolders = False, worker_factory=None) -> SimpleAsyncEventHandler:
        assert isinstance(folder, pathlib.Path), type(folder)
        assert folder.is_dir(), folder

        folder_str = str(folder)
        assert folder_str not in self.__watches, folder_str

        self.__handlers[folder_str] = handler = SimpleAsyncEventHandler(
            target_func=target_func, file_ending=file_ending, worker_factory=worker_factory
        )
        self.__watches[folder_str] = self.__observer.schedule(handler, path=folder_str, recursive=watch_subfolders)
        return handler

    def watch_folder_habapp_events(self, folder: pathlib.Path, file_ending: str, habapp_topic: str,
                                   watch_subfolders: bool = False):
        assert isinstance(folder, pathlib.Path), type(folder)
        assert folder.is_dir(), folder

        folder_str = str(folder)
        assert folder_str not in self.__watches, folder_str

        self.__handlers[folder_str] = handler = FileEventToHABAppEvent(
            folder=folder, habapp_topic=habapp_topic, file_ending=file_ending, recursive=watch_subfolders
        )
        self.__watches[folder_str] = self.__observer.schedule(handler, path=folder_str, recursive=watch_subfolders)
        return handler

    def unwatch_folder(self, folder):
        if isinstance(folder, pathlib.Path):
            folder = str(folder)
        assert isinstance(folder, str), type(folder)

        self.__handlers.pop(folder)
        self.__observer.unschedule(self.__watches.pop(folder))

    def get_handler(self, folder) -> typing.Union[SimpleAsyncEventHandler, FileEventToHABAppEvent]:
        if isinstance(folder, pathlib.Path):
            folder = str(folder)
        assert isinstance(folder, str), type(folder)

        return self.__handlers[folder]
