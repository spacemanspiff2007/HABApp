import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileMovedEvent, FileCreatedEvent, \
    FileDeletedEvent, FileModifiedEvent

import HABApp


class FileEventToHABAppEvent(FileSystemEventHandler):
    def __init__(self, folder: Path, habapp_topic: str, file_ending: str, recursive=False):
        assert isinstance(folder, Path), type(folder)
        assert isinstance(file_ending, str), type(file_ending)
        assert isinstance(habapp_topic, str), type(habapp_topic)
        assert isinstance(recursive, bool), type(recursive)

        self.folder: Path = folder
        self.habapp_topic: str = habapp_topic
        self.file_ending: str = file_ending
        self.recursive: bool = recursive

    def send_habapp_event(self, path: str, event):
        HABApp.core.EventBus.post_event(
            self.habapp_topic, event.from_path(self.folder, Path(path))
        )

    def on_deleted(self, event):
        if not isinstance(event, FileDeletedEvent):
            return None

        if not event.src_path.endswith(self.file_ending):
            return None

        self.send_habapp_event(event.src_path, HABApp.core.events.file_events.RequestFileUnloadEvent)

    def on_created(self, event):
        if not isinstance(event, FileCreatedEvent):
            return None

        if not event.src_path.endswith(self.file_ending):
            return None

        self.send_habapp_event(event.src_path, HABApp.core.events.file_events.RequestFileLoadEvent)

    def on_moved(self, event):
        if not isinstance(event, FileMovedEvent):
            return None

        if event.src_path.endswith(self.file_ending):
            self.send_habapp_event(event.src_path, HABApp.core.events.file_events.RequestFileUnloadEvent)

        if event.dest_path.endswith(self.file_ending):
            self.send_habapp_event(event.dest_path, HABApp.core.events.file_events.RequestFileLoadEvent)

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return None

        if not event.src_path.endswith(self.file_ending):
            return None

        self.send_habapp_event(event.src_path, HABApp.core.events.file_events.RequestFileLoadEvent)

    def trigger_load_for_all_files(self, delay: int = None):

        # trigger event for every file
        for f in self.folder.glob(f'**/*{self.file_ending}' if self.recursive else f'*{self.file_ending}'):
            if not f.name.endswith(self.file_ending):
                continue

            if delay is not None:
                time.sleep(delay)

            HABApp.core.EventBus.post_event(
                self.habapp_topic, HABApp.core.events.file_events.RequestFileLoadEvent.from_path(
                    folder=self.folder, file=f
                )
            )
