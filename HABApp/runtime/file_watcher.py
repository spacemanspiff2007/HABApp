from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileMovedEvent
import pathlib


class SimpleFileEventHandler(FileSystemEventHandler):
    def __init__(self, file_ending: str, callback):
        assert callable(callback)
        assert isinstance(file_ending, str), type(file_ending)
        self.__cb = callback
        self.__file_ending = file_ending

    def on_any_event(self, event: FileSystemEvent):

        src_path = event.src_path
        if src_path.endswith(self.__file_ending):
            self.__cb(pathlib.Path(src_path))

        # FileMovedEvent we have to make an additional call:
        # 1. src has been removed
        # 2. dst has been created
        if isinstance(event, FileMovedEvent):
            dest_path = event.dest_path
            if dest_path.endswith(self.__file_ending):
                self.__cb(pathlib.Path(dest_path))

        return None


class SimpleFileWatcher:
    def __init__(self):

        self.__observer = Observer()
        self.__folders = {}

        self.__started = False


    def start(self, shutdown_helper):
        from .shutdown_helper import ShutdownHelper
        assert isinstance(shutdown_helper, ShutdownHelper)

        # we shall only start once!
        assert self.__started == False
        self.__started = True

        # start watching the folders
        self.__observer.start()

        # register for proper shutdown
        shutdown_helper.register_func(self.__observer.stop)
        shutdown_helper.register_func(self.__observer.join, last=True)
        return None

    def watch_folder(self, folder: pathlib.Path, file_ending: str, callback, recursive = False):
        assert isinstance(folder, pathlib.Path)
        assert folder.is_dir()

        folder = str(folder)
        assert folder not in self.__folders, folder

        handler = SimpleFileEventHandler(file_ending=file_ending, callback=callback)
        self.__folders[folder] = self.__observer.schedule(handler, path=folder, recursive=recursive)

    def unwatch_folder(self, folder):
        if isinstance(folder, pathlib.Path):
            folder = str(folder)
        assert isinstance(folder, str), type(folder)

        self.__observer.unschedule(self.__folders[folder])
