from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileMovedEvent, FileCreatedEvent, \
    FileDeletedEvent, FileModifiedEvent


class FileEventTarget:
    def add_file(self, path: Path):
        raise NotImplementedError()

    def reload_file(self, path: Path):
        raise NotImplementedError()

    def remove_file(self, path: Path):
        raise NotImplementedError()


class SimpleFileEventHandler(FileSystemEventHandler):
    def __init__(self, event_target, file_ending: str, worker_factory=None):
        assert isinstance(event_target, FileEventTarget), type(event_target)
        self.target = event_target

        assert isinstance(file_ending, str), type(file_ending)
        self.__file_ending = file_ending

        # Possibility to use a wrapper to load files
        # do not reuse an instantiated WrappedFunction because it will throw errors in the traceback module
        self.__worker_factory = worker_factory

    def _get_func(self, func):
        if self.__worker_factory is None:
            return func
        return self.__worker_factory(func)

    def on_deleted(self, event):
        if not isinstance(event, FileDeletedEvent):
            return None

        if not event.src_path.endswith(self.__file_ending):
            return None

        self._get_func(self.target.remove_file)(Path(event.src_path))

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return None

        if not event.src_path.endswith(self.__file_ending):
            return None

        self._get_func(self.target.reload_file)(Path(event.src_path))

    def on_created(self, event):
        if not isinstance(event, FileCreatedEvent):
            return None

        if not event.src_path.endswith(self.__file_ending):
            return None

        self._get_func(self.target.add_file)(Path(event.src_path))

    def on_moved(self, event):
        if not isinstance(event, FileMovedEvent):
            return None

        if event.src_path.endswith(self.__file_ending):
            self._get_func(self.target.remove_file)(Path(event.src_path))

        if event.dest_path.endswith(self.__file_ending):
            self._get_func(self.target.add_file)(Path(event.dest_path))
