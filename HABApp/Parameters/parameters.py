import typing

_PARAMETERS: typing.Dict[str, dict] = {}


def remove_parameter_file(file):
    return _PARAMETERS.pop(file)


def set_parameter_file(file: str, value):
    _PARAMETERS[file] = value


def get_parameter_file(file: str):
    return _PARAMETERS[file]


def add_parameter(file: str, *keys, default_value):
    save = False

    if file not in _PARAMETERS:
        save = True
        _PARAMETERS[file] = param = {}
    else:
        param = _PARAMETERS[file]

    if keys:
        # Create structure
        for key in keys[:-1]:
            if key not in param:
                param[key] = {}
                save = True
            param = param[key]

        # Create value
        if keys[-1] not in param:
            param[keys[-1]] = default_value
            save = True

    if save:
        _PARAMETER_FILES.save_file(file)
    return None


def get_value(file: str, *keys):
    try:
        param = _PARAMETERS[file]
    except KeyError:
        raise FileNotFoundError(f'File {file}.yml not found in params folder!')

    # lookup parameter
    for key in keys:
        param = param[key]
    return param


# Import here to prevent cyclic imports
from .parameter_files import ParameterFileWatcher    # noqa: E402
_PARAMETER_FILES: ParameterFileWatcher = None


def setup(config, folder_watcher):
    global _PARAMETER_FILES
    _PARAMETER_FILES = ParameterFileWatcher(config, folder_watcher)
