import typing

from pydantic import BaseModel

from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.events.habapp_events import RequestFileLoadEvent
from HABApp.core.internals import uses_post_event


post_event = uses_post_event()

_PARAMETERS: dict[str, dict | list | BaseModel] = {}
_VALIDATORS: dict[str, BaseModel] = {}


def remove_parameter_file(file) -> None:
    _PARAMETERS.pop(file)


def set_parameter_file(file: str, value) -> None:
    # validate the parameters, this will raise an exception
    if model := _VALIDATORS.get(file):
        # validate and dump so we get the defaults
        value = model.model_validate(value).model_dump()

    _PARAMETERS[file] = value


def get_parameter_file(file: str):
    return _PARAMETERS[file]


def set_file_validator(filename: str, model: BaseModel | None) -> None:
    """Add a validator for the parameter file. If the file is already loaded this will reload the file.

    :param filename: filename which shall be validated (without extension)
    :param model   : Description of file content - see the library
                      `voluptuous <https://github.com/alecthomas/voluptuous#show-me-an-example/>`_ for examples.
                      Use `None` to remove validator.
    """

    # Remove validator
    if model is None:
        _VALIDATORS.pop(filename, None)
        return None

    if not isinstance(model, BaseModel):
        msg = f'Validator for {filename} must be an instance of BaseModel!'
        raise TypeError(msg)

    # Set validator
    old = _VALIDATORS.get(filename)
    _VALIDATORS[filename] = model

    if old is not None and old.model_json_schema() == model.model_json_schema():
        log.debug(f'Validator for {filename} did not change')
        return None

    log.debug(f'Validator for {filename} changed')
    post_event(TOPIC_FILES, RequestFileLoadEvent(filename))


def add_parameter(file: str, *keys, default_value):
    save = False

    if file not in _PARAMETERS:
        save = True
        param: typing.Dict[str, typing.Any] = {}
        _PARAMETERS[file] = param
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
        msg = f'File {file}.yml not found in params folder!'
        raise FileNotFoundError(msg)

    # lookup parameter
    for key in keys:
        param = param[key]
    return param


# Import here to prevent cyclic imports
from .parameter_files import log, save_file  # noqa: E402
