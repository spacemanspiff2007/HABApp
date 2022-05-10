import logging
import threading
from pathlib import Path

import HABApp
from HABApp.core.files.file import HABAppFile
from HABApp.core.files.folders import add_folder as add_habapp_folder
from .parameters import get_parameter_file, remove_parameter_file, set_parameter_file

log = logging.getLogger('HABApp.RuleParameters')

LOCK = threading.Lock()
PARAM_PREFIX = 'params/'


async def load_file(name: str, path: Path):
    with LOCK:  # serialize to get proper error messages
        with path.open(mode='r', encoding='utf-8') as file:
            data = HABApp.core.const.yml.load(file)
        if data is None:
            data = {}
        set_parameter_file(path.stem, data)

    log.debug(f'Loaded params from {name}!')


async def unload_file(name: str, path: Path):
    with LOCK:  # serialize to get proper error messages
        remove_parameter_file(path.stem)

    log.debug(f'Removed params from {path.name}!')


def save_file(file: str):
    assert isinstance(file, str), type(file)
    path = HABApp.CONFIG.directories.param
    if path is None:
        raise ValueError('Parameter files are disabled! Configure a folder to use them!')

    filename = path / (file + '.yml')

    with LOCK:  # serialize to get proper error messages
        log.info(f'Updated {filename}')
        with filename.open('w', encoding='utf-8') as outfile:
            HABApp.core.const.yml.dump(get_parameter_file(file), outfile)


class HABAppParameterFile(HABAppFile):
    LOGGER = log
    LOAD_FUNC = load_file
    UNLOAD_FUNC = unload_file


async def setup_param_files() -> bool:
    path = HABApp.CONFIG.directories.param
    if path is None:
        return False

    folder = add_habapp_folder(PARAM_PREFIX, path, 100)
    folder.add_file_type(HABAppParameterFile)
    watcher = folder.add_watch('.yml')
    await watcher.trigger_all()


def reload_param_file(name: str):
    name = f'{PARAM_PREFIX}{name}.yml'
    path = HABApp.core.files.folders.get_path(name)
    HABApp.core.asyncio.create_task(HABApp.core.files.manager.process_file(name, path))
