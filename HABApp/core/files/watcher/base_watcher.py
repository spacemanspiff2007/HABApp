from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler


class BaseWatcher(FileSystemEventHandler):
    def __init__(self, folder: Path, file_ending: str, watch_subfolders: bool = False):
        assert isinstance(folder, Path), type(folder)
        assert isinstance(file_ending, str), type(file_ending)
        assert watch_subfolders is True or watch_subfolders is False

        self.folder: Path = folder
        self.file_ending: str = file_ending
        self.watch_subfolders: bool = watch_subfolders

    def dispatch(self, event: FileSystemEvent):
        # we don't process directory events
        if event.is_directory:
            return None

        src = event.src_path
        if src.endswith(self.file_ending):
            self.file_changed(src)

        # moved events have a dst, so we process it, too
        if hasattr(event, 'dest_path'):
            dst = event.dest_path
            if dst.endswith(self.file_ending):
                self.file_changed(dst)
        return None

    def file_changed(self, dst: str):
        raise NotImplementedError()
