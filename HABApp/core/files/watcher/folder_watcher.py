from pathlib import Path
from threading import Lock
from typing import Optional, Dict

from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from .base_watcher import BaseWatcher

LOCK = Lock()

OBSERVER: Optional[Observer] = None
WATCHES: Dict[str, ObservedWatch] = {}


def start(shutdown_helper):
    global OBSERVER

    # start only once!
    assert OBSERVER is None

    from HABApp.runtime.shutdown_helper import ShutdownHelper
    assert isinstance(shutdown_helper, ShutdownHelper)

    OBSERVER = Observer()
    OBSERVER.start()

    # register for proper shutdown
    shutdown_helper.register_func(OBSERVER.stop)
    shutdown_helper.register_func(OBSERVER.join, last=True)
    return None


def add_folder_watch(handler: BaseWatcher):
    assert OBSERVER is not None
    assert isinstance(handler, BaseWatcher), type(handler)
    assert isinstance(handler.folder, Path) and handler.folder.is_dir()

    with LOCK:
        _folder = str(handler.folder)
        assert _folder not in WATCHES

        WATCHES[_folder] = OBSERVER.schedule(handler, _folder, recursive=handler.watch_subfolders)


def remove_folder_watch(folder: Path):
    assert OBSERVER is not None
    assert isinstance(folder, Path)

    with LOCK:
        OBSERVER.unschedule(WATCHES.pop(str(folder)))
