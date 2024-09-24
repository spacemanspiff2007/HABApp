import logging
from pathlib import Path
from threading import Lock

from watchdog.observers import Observer
from watchdog.observers.api import ObservedWatch

from HABApp.core import shutdown

from .base_watcher import FileSystemEventHandler


log = logging.getLogger('HABApp.files.watcher')

LOCK = Lock()

OBSERVER: Observer | None = None
WATCHES: dict[str, ObservedWatch] = {}


def start():
    global OBSERVER

    # start only once!
    assert OBSERVER is None

    OBSERVER = Observer()
    OBSERVER.start()

    # register for proper shutdown
    shutdown.register(OBSERVER.stop, msg='Stopping folder observer')
    shutdown.register(OBSERVER.join, last=True, msg='Joining folder observer threads')
    return None


def add_folder_watch(handler: FileSystemEventHandler) -> None:
    assert OBSERVER is not None
    assert isinstance(handler, FileSystemEventHandler), type(handler)
    assert isinstance(handler.folder, Path) and handler.folder.is_dir()

    log.debug(
        f'Adding {"recursive " if handler.watch_subfolders else ""}watcher for {handler.folder} with {handler.filter}'
    )

    with LOCK:
        _folder = str(handler.folder)
        assert _folder not in WATCHES

        WATCHES[_folder] = OBSERVER.schedule(handler, _folder, recursive=handler.watch_subfolders)


def remove_folder_watch(folder: Path) -> None:
    assert OBSERVER is not None
    assert isinstance(folder, Path)

    with LOCK:
        OBSERVER.unschedule(WATCHES.pop(str(folder)))
