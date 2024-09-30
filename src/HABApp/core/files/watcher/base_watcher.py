import logging
from pathlib import Path

from watchdog.events import EVENT_TYPE_CLOSED as WD_EVENT_TYPE_CLOSED
from watchdog.events import EVENT_TYPE_CLOSED_NO_WRITE as WD_EVENT_TYPE_CLOSED_NO_WRITE
from watchdog.events import EVENT_TYPE_OPENED as WD_EVENT_TYPE_OPENED
from watchdog.events import FileSystemEvent


log = logging.getLogger('HABApp.file.events')
log.setLevel(logging.INFO)


class EventFilterBase:
    def notify(self, path: str) -> bool:
        raise NotImplementedError()


class FileEndingFilter(EventFilterBase):
    def __init__(self, ending: str) -> None:
        self.ending: str = ending

    def notify(self, path: str) -> bool:
        return path.endswith(self.ending)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ending: {self.ending}>'


class FileSystemEventHandler:
    def __init__(self, folder: Path, filter: EventFilterBase, watch_subfolders: bool = False) -> None:
        assert isinstance(folder, Path), type(folder)
        assert watch_subfolders is True or watch_subfolders is False

        self.folder: Path = folder
        self.watch_subfolders: bool = watch_subfolders

        self.filter: EventFilterBase = filter

    def dispatch(self, event: FileSystemEvent):
        log.debug(event)

        # we don't process directory events
        if event.is_directory:
            return None

        # we don't process open and close events
        if event.event_type in (WD_EVENT_TYPE_OPENED, WD_EVENT_TYPE_CLOSED, WD_EVENT_TYPE_CLOSED_NO_WRITE):
            return None

        src = event.src_path
        if self.filter.notify(src):
            self.file_changed(src)

        # moved events have a dst, so we process it, too
        if hasattr(event, 'dest_path'):
            dst = event.dest_path
            if self.filter.notify(dst):
                self.file_changed(dst)
        return None

    def file_changed(self, dst: str):
        raise NotImplementedError()
