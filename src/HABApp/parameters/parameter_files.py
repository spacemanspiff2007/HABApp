import logging
import re
import threading
from pathlib import Path

import HABApp
from HABApp.core.files.file import HABAppFile
from HABApp.core.internals.proxy import uses_file_manager

from .parameters import get_parameter_file, remove_parameter_file, set_parameter_file


log = logging.getLogger('HABApp.RuleParameters')

LOCK = threading.Lock()
PARAM_PREFIX = 'params/'

file_manager = uses_file_manager()


async def load_file(name: str, path: Path) -> None:
    with LOCK:  # serialize to get proper error messages
        with path.open(mode='r', encoding='utf-8') as file:
            data = HABApp.core.const.yml.load(file)
        if data is None:
            data = {}
        set_parameter_file(path.stem, data)

    log.debug(f'Loaded params from {name}!')


async def unload_file(name: str, path: Path) -> None:
    with LOCK:  # serialize to get proper error messages
        remove_parameter_file(path.stem)

    log.debug(f'Removed params from {path.name}!')


def save_file(file: str):
    assert isinstance(file, str), type(file)
    path = HABApp.CONFIG.directories.param
    if path is None:
        msg = 'Parameter files are disabled! Configure a folder to use them!'
        raise ValueError(msg)

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

    prefix = 'params/'
    file_manager.add_handler('ParamFiles', log, prefix=prefix, on_load=load_file, on_unload=unload_file)
    file_manager.add_folder(
        prefix, path, priority=100, pattern=re.compile(r'.yml$', re.IGNORECASE), name='rules-parameters'
    )

    return True


def reload_param_file(name: str) -> None:
    name = f'{PARAM_PREFIX}{name}.yml'
    path = HABApp.core.files.folders.get_path(name)
    HABApp.core.asyncio.create_task(HABApp.core.files.manager.process_file(name, path))
