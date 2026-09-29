from __future__ import annotations

import logging
import re
from copy import deepcopy
from io import StringIO
from typing import TYPE_CHECKING, Any, Final

from pydantic import BaseModel, ValidationError

from HABApp.core.const import yml
from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.events.habapp_events import RequestFileLoadEvent
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from pathlib import Path

    from HABApp.config import ApplicationConfig
    from HABApp.core.files import FileManager
    from HABApp.core.internals import EventBus


log = logging.getLogger('HABApp.RuleParameters')

PARAMS_PREFIX: Final = 'params/'
PARAMS_SUFFIX: Final = '.yml'


def get_user_name(name: str) -> str:
    if name.lower().startswith(PARAMS_PREFIX):
        name = name[len(PARAMS_PREFIX):]
    if name.lower().endswith(PARAMS_SUFFIX):
        name = name[:-len(PARAMS_SUFFIX)]
    return name


def _set_default_value(data: dict[str, Any], keys: tuple[str | float, ...], default_value: Any) -> bool:
    if not keys:
        return False

    changed: bool = False
    param: dict = data
    for key in keys[:-1]:
        if key not in param:
            param[key] = {}
            changed = True
        param = param[key]

    if keys[-1] not in param:
        param[keys[-1]] = default_value
        changed = True

    return changed


def _log_validation_error(path: Path, e: ValidationError) -> None:
    log.error(f'Validation of parameter file "{path}" failed:')
    for line in str(e).splitlines():
        log.error(f'  {line}')


class ParameterFile:
    __slots__ = ('data', 'name', 'path')

    def __init__(self, name: str, path: Path) -> None:
        self.name: Final = name
        self.path: Final = path
        self.data: dict[str, Any] = {}

    def get_value(self, *keys: str | float) -> Any:
        value = self.data

        for key in keys:
            value = value[key]
        return value

    def save(self) -> None:
        log.info(f'Updating {self.path}')

        # Dump first. If this fails (e.g. because the data contains something that is not yaml serializable)
        # the file on disk is left untouched.
        buffer: Final = StringIO()
        yml.dump(self.data, buffer)

        self.path.write_text(buffer.getvalue(), encoding='utf-8')


class ParameterRegistry:
    __slots__ = ('_config', '_event_bus', '_files', '_validators')

    def __init__(self, config: ApplicationConfig, event_bus: EventBus) -> None:
        self._config: Final = config
        self._event_bus: Final = event_bus

        self._files: Final[dict[str, ParameterFile]] = {}
        self._validators: Final[dict[str, type[BaseModel]]] = {}

    def setup(self, file_manager: FileManager) -> bool:
        path = self._config.directories.params
        if path is None:
            return False

        regex: Final = re.compile(re.escape(PARAMS_SUFFIX) + '$', re.IGNORECASE)

        file_manager.add_handler(
            self.__class__.__name__, log, prefix=PARAMS_PREFIX,
            on_load=self._on_load, on_unload=self._on_unload
        )
        file_manager.add_folder(
            PARAMS_PREFIX, path, priority=100, pattern=regex, name='rules-parameters'
        )
        return True

    # ------------------------------------------------------------------------------------------------------------------
    # file manager api
    # ------------------------------------------------------------------------------------------------------------------
    async def _on_load(self, name: str, path: Path) -> None:
        with path.open(mode='r', encoding='utf-8') as file:
            file_data: dict[str, Any] | None = yml.load(file)

        data: dict[str, Any] = file_data if file_data is not None else {}
        user_name: Final = get_user_name(name)

        try:
            data = self._validate(user_name, data)
        except ValidationError as e:
            _log_validation_error(path, e)
            raise

        file_obj = self._files.get(user_name)
        if file_obj is None:
            self._files[user_name] = file_obj = ParameterFile(user_name, path)

        file_obj.data = data
        log.debug(f'Successfully loaded {name}!')

    async def _on_unload(self, name: str, path: Path) -> None:  # noqa: ARG002
        user_name = get_user_name(name)
        self._files.pop(user_name, None)
        log.debug(f'Removed {user_name}!')

    def _validate(self, name: str, value: dict[str, Any]) -> dict[str, Any]:
        if (model := self._validators.get(name)) is not None:
            # validate and dump so we get the defaults
            value = model.model_validate(value).model_dump()
        return value

    # ------------------------------------------------------------------------------------------------------------------
    # public api
    # ------------------------------------------------------------------------------------------------------------------
    def get_value(self, file: str, *keys: str | float) -> Any:
        try:
            file_obj: Final = self._files[file]
        except KeyError:
            msg = f'File {file}.yml not found in params folder!'
            raise FileNotFoundError(msg) from None

        return file_obj.get_value(*keys)

    def _get_or_create_file(self, file: str) -> ParameterFile:
        file_obj = self._files.get(file)
        if file_obj is None:
            path = self._config.directories.params
            if path is None:
                msg = 'Parameter files are disabled! Configure a folder to use them!'
                raise ValueError(msg)
            self._files[file] = file_obj = ParameterFile(file, path / (file + PARAMS_SUFFIX))
        return file_obj

    def add_parameter(self, file: str, *keys: str | float, default_value: Any) -> None:
        file_obj: Final = self._get_or_create_file(file)

        # Work on a copy so the registry never ends up in an inconsistent/invalid state:
        # first mutate & validate the copy, only commit and save if that succeeded.
        new_data = deepcopy(file_obj.data)
        if not isinstance(new_data, dict):
            msg = f'Parameter file "{file}" does not contain a dictionary, can not add a default value!'
            raise TypeError(msg)

        if not _set_default_value(new_data, keys, default_value):
            return None

        try:
            new_data = self._validate(file, new_data)
        except ValidationError as e:
            _log_validation_error(file_obj.path, e)
            raise

        file_obj.data = new_data
        file_obj.save()
        return None

    def set_validator(self, filename: str, model: type[BaseModel] | None) -> None:
        """Add a validator for the parameter file. If the file is already loaded this will reload the file.

        :param filename: filename which shall be validated (without extension)
        :param model: Pydantic model class describing the file content. Use ``None`` to remove the validator.
        """
        # Remove validator
        if model is None:
            self._validators.pop(filename, None)
            return None

        if not (isinstance(model, type) and issubclass(model, BaseModel)):
            msg = f'Validator for {filename} must be a subclass of BaseModel!'
            raise TypeError(msg)

        # Set validator
        old: Final = self._validators.get(filename)
        self._validators[filename] = model

        if old is not None and old.model_json_schema() == model.model_json_schema():
            log.debug(f'Validator for {filename} did not change')
            return None

        log.debug(f'Validator for {filename} changed')
        self._event_bus.post_event(TOPIC_FILES, RequestFileLoadEvent(filename))
        return None


@HABAPP_PROVIDER.register
async def _provide_registry(config: ApplicationConfig, file_manager: FileManager,
                            event_bus: EventBus) -> ParameterRegistry:
    obj = ParameterRegistry(config, event_bus)
    obj.setup(file_manager)
    return obj


def set_file_validator(filename: str, model: type[BaseModel] | None) -> None:
    """Add a validator for the parameter file. If the file is already loaded this will reload the file.

    :param filename: filename which shall be validated (without extension)
    :param model: Pydantic model class describing the file content. Use ``None`` to remove the validator.
    """
    HABAPP_PROVIDER.get_existing(ParameterRegistry).set_validator(filename, model)
