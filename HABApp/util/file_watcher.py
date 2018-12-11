import pathlib

from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileMovedEvent


class SimpleFileWatcher(FileSystemEventHandler):
    def __init__(self, callback, file_ending : str):
        assert callable(callback)
        assert isinstance(file_ending, str), type(file_ending)
        self.__cb = callback

        self.__ending = file_ending

    def on_any_event(self, event: FileSystemEvent):
        # dumme events rausfiltern
        src_path = getattr(event, 'src_path', '')

        # nur FileMovedEvent hat dest_path
        if isinstance(event, FileMovedEvent):
            if not event.dest_path.endswith(self.__ending):
                return None
            path = pathlib.Path(event.dest_path)
        else:
            if not src_path.endswith(self.__ending):
                return
            path = pathlib.Path(src_path)

        self.__cb(path)
