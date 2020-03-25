import time
from pathlib import Path

import HABApp
from .simpleasyncfileevent import SimpleAsyncEventHandler


class FileEventToHABAppEvent(SimpleAsyncEventHandler):
    def __init__(self, folder: Path, habapp_topic: str, file_ending: str, recursive=False):
        assert isinstance(folder, Path), type(folder)
        assert isinstance(file_ending, str), type(file_ending)
        assert isinstance(habapp_topic, str), type(habapp_topic)
        assert isinstance(recursive, bool), type(recursive)

        super().__init__(self.create_habapp_event, file_ending)

        self.folder: Path = folder
        self.habapp_topic: str = habapp_topic
        self.recursive: bool = recursive

    def create_habapp_event(self, path: Path):
        if path.is_file():
            event = HABApp.core.events.habapp_events.RequestFileLoadEvent
        else:
            event = HABApp.core.events.habapp_events.RequestFileUnloadEvent

        HABApp.core.EventBus.post_event(
            self.habapp_topic, event.from_path(self.folder, path)
        )

    @HABApp.core.wrapper.log_exception
    def trigger_load_for_all_files(self, delay: int = None):

        # trigger event for every file, we load in alphabetical order
        rule_files = self.folder.glob(f'**/*{self.file_ending}' if self.recursive else f'*{self.file_ending}')
        for f in sorted(rule_files, key=lambda x: x.relative_to(self.folder)):
            if not f.name.endswith(self.file_ending):
                continue

            if delay is not None:
                time.sleep(delay)

            HABApp.core.EventBus.post_event(
                self.habapp_topic, HABApp.core.events.habapp_events.RequestFileLoadEvent.from_path(
                    folder=self.folder, file=f
                )
            )
