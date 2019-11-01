import HABApp
import typing

import voluptuous

_PARAMETERS: typing.Dict[str, dict] = {}
_VALIDATORS: typing.Dict[str, voluptuous.Schema] = {}


def remove_parameter_file(file):
    return _PARAMETERS.pop(file)


def set_parameter_file(file: str, value):
    # validate the parameters, this will raise an exception
    validator = _VALIDATORS.get(file)
    if validator is not None:
        value = validator(value)

    _PARAMETERS[file] = value


def get_parameter_file(file: str):
    return _PARAMETERS[file]


def set_file_validator(file: str, validator: typing.Any, allow_extra_keys=True):

    # Remove validator
    if validator is None:
        _VALIDATORS.pop(file, None)
        return

    # Set validator
    old_validator = _VALIDATORS.get(file)
    _VALIDATORS[file] = new_validator = voluptuous.Schema(
        validator, required=True, extra=(voluptuous.ALLOW_EXTRA if allow_extra_keys else voluptuous.PREVENT_EXTRA)
    )

    # todo: move this to file handling so we get the extension
    if old_validator != new_validator:
        HABApp.core.EventBus.post_event(
            HABAPP_PARAM_TOPIC, HABApp.core.events.habapp_events.RequestFileLoadEvent(file + '.yml')
        )



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
        save_file(file)
    return None


def get_value(file: str, *keys) -> typing.Any:
    try:
        param = _PARAMETERS[file]
    except KeyError:
        raise FileNotFoundError(f'File {file}.yml not found in params folder!')

    # lookup parameter
    for key in keys:
        param = param[key]
    return param


# Import here to prevent cyclic imports
from .parameter_files import save_file, HABAPP_PARAM_TOPIC  # noqa: E402
