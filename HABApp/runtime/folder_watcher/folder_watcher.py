import pathlib

from watchdog.observers import Observer

from .fileeventhandler import SimpleFileEventHandler


class FolderWatcher:
    def __init__(self):

        self.__observer = Observer()
        self.__folders = {}

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

    def watch_folder(self, folder: pathlib.Path, file_ending: str, event_target,
                     watch_subfolders = False, worker_factory=None):
        assert isinstance(folder, pathlib.Path), type(folder)
        assert folder.is_dir(), folder

        folder = str(folder)
        assert folder not in self.__folders, folder

        handler = SimpleFileEventHandler(event_target=event_target, file_ending=file_ending,
                                         worker_factory=worker_factory)
        self.__folders[folder] = self.__observer.schedule(handler, path=folder, recursive=watch_subfolders)

    def unwatch_folder(self, folder):
        if isinstance(folder, pathlib.Path):
            folder = str(folder)
        assert isinstance(folder, str), type(folder)

        self.__observer.unschedule(self.__folders.pop(folder))
