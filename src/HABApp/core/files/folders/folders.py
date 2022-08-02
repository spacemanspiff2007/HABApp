from pathlib import Path
from typing import Dict
from typing import List, Type

import HABApp
from HABApp.core.const.topics import TOPIC_FILES as T_FILES
from HABApp.core.events.habapp_events import RequestFileUnloadEvent, RequestFileLoadEvent
from ..watcher import AggregatingAsyncEventHandler
from HABApp.core.internals import uses_post_event

FOLDERS: Dict[str, 'ConfiguredFolder'] = {}

post_event = uses_post_event()


async def _generate_file_events(files: List[Path]):
    for file in files:
        name = get_name(file)
        post_event(T_FILES, RequestFileLoadEvent(name) if file.is_file() else RequestFileUnloadEvent(name))


class ConfiguredFolder:
    def __init__(self, prefix: str, folder: Path, priority: int):
        self.prefix = prefix
        self.folder = folder
        self.priority: int = priority   # priority determines the order how the files will be loaded

    def add_watch(self, file_ending: str, watch_subfolders: bool = True) -> AggregatingAsyncEventHandler:
        filter = HABApp.core.files.watcher.FileEndingFilter(file_ending)
        handler = AggregatingAsyncEventHandler(self.folder, _generate_file_events, filter, watch_subfolders)
        HABApp.core.files.watcher.add_folder_watch(handler)
        return handler

    def add_file_type(self, cls: Type['HABApp.core.files.file.HABAppFile']):
        HABApp.core.files.file.register_file_type(self.prefix, cls)


def get_prefixes() -> List[str]:
    return list(map(lambda x: x.prefix, sorted(FOLDERS.values(), key=lambda x: x.priority, reverse=True)))


def add_folder(prefix: str, folder: Path, priority: int) -> ConfiguredFolder:
    """Make a folder known

    :param prefix: HABApp file name prefix
    :param folder: Folder path
    :param priority: Priority (used to determine the load order)
    :return: ConfiguredFolder
    """
    assert prefix and prefix.endswith('/')
    for obj in FOLDERS.values():
        assert obj.priority != priority
    FOLDERS[prefix] = c = ConfiguredFolder(prefix, folder, priority)
    return c


def get_name(path: Path) -> str:
    path_str = path.as_posix()
    for prefix, cfg in sorted(FOLDERS.items(), key=lambda x: len(x[0]), reverse=True):
        folder = cfg.folder.as_posix()
        if path_str.startswith(folder):
            return prefix + path_str[len(folder) + 1:]

    raise ValueError(f'Path "{path_str}" is not part of the configured folders!')


def get_path(name: str) -> Path:
    for prefix, obj in FOLDERS.items():
        if name.startswith(prefix):
            return obj.folder / name[len(prefix):]

    raise ValueError(f'Prefix not found for "{name}"!')
