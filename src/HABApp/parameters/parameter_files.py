import logging
import re
from pathlib import Path
from typing import Final

import HABApp
from HABApp.core.files.file import HABAppFile
from HABApp.core.internals.proxy import uses_file_manager

from .parameters import get_parameter_file, remove_parameter_file, set_parameter_file


log = logging.getLogger('HABApp.RuleParameters')

PARAMS_PREFIX: Final = 'params/'
PARAMS_SUFFIX: Final = '.yml'

file_manager = uses_file_manager()


def get_user_name(name: str) -> str:
    return name.removeprefix(PARAMS_PREFIX).removesuffix(PARAMS_SUFFIX)


async def load_file(name: str, path: Path) -> None:
    with path.open(mode='r', encoding='utf-8') as file:
        data = HABApp.core.const.yml.load(file)
    if data is None:
        data = {}

    user_name = get_user_name(name)
    set_parameter_file(user_name, data)

    log.debug(f'Successfully loaded {name}!')


async def unload_file(name: str, path: Path) -> None:
    user_name = get_user_name(name)
    remove_parameter_file(user_name)
    log.debug(f'Removed {user_name}!')


def save_file(file: str):
    assert isinstance(file, str), type(file)
    path = HABApp.CONFIG.directories.params
    if path is None:
        msg = 'Parameter files are disabled! Configure a folder to use them!'
        raise ValueError(msg)

    filename = path / (file + '.yml')

    log.info(f'Updated {filename}')
    with filename.open('w', encoding='utf-8') as outfile:
        HABApp.core.const.yml.dump(get_parameter_file(file), outfile)


class HABAppParameterFile(HABAppFile):
    LOGGER = log
    LOAD_FUNC = load_file
    UNLOAD_FUNC = unload_file


async def setup_param_files() -> bool:
    path = HABApp.CONFIG.directories.params
    if path is None:
        return False

    regex = re.escape(PARAMS_SUFFIX) + '$'

    file_manager.add_handler('ParamFiles', log, prefix=PARAMS_PREFIX, on_load=load_file, on_unload=unload_file)
    file_manager.add_folder(
        PARAMS_PREFIX, path, priority=100, pattern=re.compile(regex, re.IGNORECASE), name='rules-parameters'
    )

    return True
