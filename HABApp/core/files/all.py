from __future__ import annotations

import logging
import typing
from itertools import chain
from pathlib import Path
from threading import Lock

import HABApp
from HABApp.core.wrapper import ignore_exception
from . import name_from_path
from .file import HABAppFile
from .watcher import AggregatingAsyncEventHandler

log = logging.getLogger('HABApp.files')

LOCK = Lock()

ALL: typing.Dict[str, HABAppFile] = {}


@ignore_exception
def process(files: typing.List[Path], load_next: bool = True):

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

    if load_next:
        _load_next()


@ignore_exception
def file_load_ok(name: str):
    with LOCK:
        f = ALL.get(name)
    f.load_ok()

    _load_next()


@ignore_exception
def file_load_failed(name: str):
    with LOCK:
        f = ALL.get(name)
    f.load_failed()

    _load_next()


@ignore_exception
def _load_next():

    # check files for dependencies etc.
    for file in list(filter(lambda x: not x.is_checked, ALL.values())):
        try:
            file.check_properties()
        except Exception:
            pass

    # Load order is parameters -> openhab config files-> rules
    f_n = HABApp.core.files.file_name
    _all = sorted(ALL.keys())
    files = chain(filter(f_n.is_param, _all), filter(f_n.is_config, _all), filter(f_n.is_rule, _all))

    missing_deps = []
    for name in files:
        file = ALL[name]
        if file.is_loaded:
            continue

        if file.can_be_loaded():
            file.load()
            return None
        else:
            missing_deps.append(file)

    if missing_deps:
        warn = HABApp.core.logger.HABAppWarning(log)
        warn.add('The following files could not be loaded because they have missing dependencies:')
        for f in missing_deps:
            warn.add(' - {} ({})', f.name, ", ".join(f.properties.depends_on))
        warn.dump()


def watch_folder(folder: Path, file_ending: str, watch_subfolders: bool = False) -> AggregatingAsyncEventHandler:
    handler = AggregatingAsyncEventHandler(folder, process, file_ending, watch_subfolders)
    HABApp.core.files.watcher.add_folder_watch(handler)
    return handler
