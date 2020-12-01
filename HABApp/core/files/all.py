import logging
import typing
from itertools import chain
from pathlib import Path
from threading import Lock

import HABApp
from HABApp.core.wrapper import ignore_exception
from . import name_from_path
from .file import CircularReferenceError, HABAppFile
from .watcher import AggregatingAsyncEventHandler

log = logging.getLogger('HABApp.files')

LOCK = Lock()

ALL: typing.Dict[str, HABAppFile] = {}
LOAD_RUNNING = False


def process(files: typing.List[Path], load_next: bool = True):
    global LOAD_RUNNING

    for file in files:
        name = name_from_path(file)

        # unload
        if not file.is_file():
            with LOCK:
                existing = ALL.pop(name, None)
            if existing is not None:
                existing.unload()
            continue

        # reload/initial load
        obj = HABAppFile.from_path(name, file)
        with LOCK:
            ALL[name] = obj

    if not load_next:
        return None

    # Start loading only once
    with LOCK:
        if LOAD_RUNNING:
            return None
        LOAD_RUNNING = True

    _load_next()


@ignore_exception
def file_load_ok(name: str):
    with LOCK:
        file = ALL.get(name)
    file.load_ok()

    # reload files with the property "reloads_on"
    reload = [k.path for k in filter(lambda f: f.is_loaded and name in f.properties.reloads_on, ALL.values())]
    if reload:
        process(reload, load_next=False)

    _load_next()


@ignore_exception
def file_load_failed(name: str):
    with LOCK:
        f = ALL.get(name)
    f.load_failed()

    _load_next()


def _load_next():
    global LOAD_RUNNING

    # check files for dependencies etc.
    for file in list(filter(lambda x: not x.is_checked, ALL.values())):
        try:
            file.check_properties()
        except Exception as e:
            if not isinstance(e, (CircularReferenceError, FileNotFoundError)):
                HABApp.core.wrapper.process_exception(file.check_properties, e, logger=log)

    # Load order is parameters -> openhab config files-> rules
    f_n = HABApp.core.files.file_name
    _all = sorted(ALL.keys())
    files = chain(filter(f_n.is_param, _all), filter(f_n.is_config, _all), filter(f_n.is_rule, _all))

    for name in files:
        file = ALL[name]
        if file.is_loaded or file.is_failed:
            continue

        if file.can_be_loaded():
            file.load()
            return None

    with LOCK:
        LOAD_RUNNING = False


def watch_folder(folder: Path, file_ending: str, watch_subfolders: bool = False) -> AggregatingAsyncEventHandler:
    handler = AggregatingAsyncEventHandler(folder, process, file_ending, watch_subfolders)
    HABApp.core.files.watcher.add_folder_watch(handler)
    return handler
