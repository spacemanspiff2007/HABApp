import HABApp
from pathlib import Path


PREFIX_CONFIGS = 'configs'
PREFIX_PARAMS = 'params'
PREFIX_RULES = 'rules'


def name_from_path(path: Path) -> str:
    _path = path.as_posix()
    d = HABApp.config.CONFIG.directories
    folders = {PREFIX_CONFIGS: d.config.as_posix(), PREFIX_PARAMS: d.param.as_posix(), PREFIX_RULES: d.rules.as_posix()}

    for prefix, folder in folders.items():
        if _path.startswith(folder):
            return prefix + '/' + _path[len(folder) + 1:]

    raise ValueError(f'Path "{path}" is not part of the configured folders!')


def path_from_name(name: str) -> Path:
    d = HABApp.config.CONFIG.directories
    folders = {PREFIX_CONFIGS: d.config.as_posix(), PREFIX_PARAMS: d.param.as_posix(), PREFIX_RULES: d.rules.as_posix()}

    for prefix, folder in folders.items():
        if name.startswith(prefix):
            return Path(folder + '/' + name[len(prefix):])

    raise ValueError(f'Prefix not found for "{name}"!')


def is_config(name: str):
    return name.startswith(PREFIX_CONFIGS)


def is_param(name: str):
    return name.startswith(PREFIX_PARAMS)


def is_rule(name: str):
    return name.startswith(PREFIX_RULES)
