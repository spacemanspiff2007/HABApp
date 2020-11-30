import HABApp
from pathlib import Path


_PRE_CONFIGS = 'configs'
_PRE_PARAMS = 'params'
_PRE_RULES = 'rules'


def name_from_path(path: Path) -> str:
    _path = path.as_posix()
    d = HABApp.config.CONFIG.directories
    folders = {_PRE_CONFIGS: d.config.as_posix(), _PRE_PARAMS: d.param.as_posix(), _PRE_RULES: d.rules.as_posix()}

    for prefix, folder in folders.items():
        if _path.startswith(folder):
            return prefix + '/' + _path[len(folder) + 1:]

    raise ValueError(f'Path "{path}" is not part of the configured folders!')


def path_from_name(name: str) -> Path:
    d = HABApp.config.CONFIG.directories
    folders = {_PRE_CONFIGS: d.config.as_posix(), _PRE_PARAMS: d.param.as_posix(), _PRE_RULES: d.rules.as_posix()}

    for prefix, folder in folders.items():
        if name.startswith(prefix):
            return Path(folder + '/' + name[len(prefix):])

    raise ValueError(f'Prefix not found for "{name}"!')


def is_config(name: str):
    return name.startswith(_PRE_CONFIGS)


def is_param(name: str):
    return name.startswith(_PRE_PARAMS)


def is_rule(name: str):
    return name.startswith(_PRE_RULES)
