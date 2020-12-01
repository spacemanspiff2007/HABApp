import logging
import threading
from pathlib import Path

import HABApp
from HABApp.core.files import file_load_failed, file_load_ok
from .parameters import get_parameter_file, remove_parameter_file, set_parameter_file

log = logging.getLogger('HABApp.RuleParameters')

LOCK = threading.Lock()


def setup_param_files() -> bool:
    if not HABApp.CONFIG.directories.param.is_dir():
        log.info(f'Parameter files disabled: Folder {HABApp.CONFIG.directories.param} does not exist!')
        return False

    # Add event bus listener
    HABApp.core.files.add_event_bus_listener('param', load_file, unload_file, log)

    # watch folder and load all files
    watcher = HABApp.core.files.watch_folder(HABApp.CONFIG.directories.param, '.yml', True)
    watcher.trigger_all()
    return True


def load_file(name: str, path: Path):
    with LOCK:  # serialize to get proper error messages
        try:
            with path.open(mode='r', encoding='utf-8') as file:
                data = HABApp.core.const.yml.load(file)
            if data is None:
                data = {}
            set_parameter_file(path.stem, data)
        except Exception as exc:
            e = HABApp.core.logger.HABAppError(log)
            e.add(f"Could not load parameters for {name} ({path})!")
            e.add_exception(exc, add_traceback=True)
            e.dump()

            file_load_failed(name)
            return None

    log.debug(f'Loaded params from {path.name}!')
    file_load_ok(name)


def unload_file(name: str, path: Path):
    with LOCK:  # serialize to get proper error messages
        try:
            remove_parameter_file(path.stem)
        except Exception as exc:
            e = HABApp.core.logger.HABAppError(log)
            e.add(f"Could not remove parameters for {name} ({path})!")
            e.add_exception(exc, add_traceback=True)
            e.dump()
            return None

        log.debug(f'Removed params from {path.name}!')


def save_file(file: str):
    assert isinstance(file, str), type(file)
    filename = HABApp.CONFIG.directories.param / (file + '.yml')

    with LOCK:  # serialize to get proper error messages
        log.info(f'Updated {filename}')
        with filename.open('w', encoding='utf-8') as outfile:
            HABApp.core.const.yml.dump(get_parameter_file(file), outfile)
