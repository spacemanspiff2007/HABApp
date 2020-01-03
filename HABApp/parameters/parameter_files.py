import logging
import threading
import traceback

import ruamel.yaml

import HABApp
from .parameters import get_parameter_file, remove_parameter_file, set_parameter_file

log = logging.getLogger('HABApp.RuleParameters')

_yml_setup = ruamel.yaml.YAML()
_yml_setup.default_flow_style = False
_yml_setup.default_style = False    # type: ignore
_yml_setup.width = 1000000          # type: ignore
_yml_setup.allow_unicode = True
_yml_setup.sort_base_mapping_type_on_output = False     # type: ignore

LOCK = threading.Lock()


def setup_param_files() -> bool:

    if not HABApp.CONFIG.directories.param.is_dir():
        log.info(f'Parameter files disabled: Folder {HABApp.CONFIG.directories.param} does not exist!')
        return False

    # listener to remove parameters
    HABApp.core.EventBus.add_listener(
        HABApp.core.EventBusListener(
            HABApp.core.events.habapp_events.TOPIC_PARAM,
            HABApp.core.WrappedFunction(load_file),
            HABApp.core.events.habapp_events.RequestFileUnloadEvent
        )
    )
    # listener to add parameters
    HABApp.core.EventBus.add_listener(
        HABApp.core.EventBusListener(
            HABApp.core.events.habapp_events.TOPIC_PARAM,
            HABApp.core.WrappedFunction(load_file),
            HABApp.core.events.habapp_events.RequestFileLoadEvent
        )
    )
    return True


def load_file(event: HABApp.core.events.habapp_events.RequestFileLoadEvent):
    path = event.get_path(HABApp.CONFIG.directories.param)

    with LOCK:  # serialize to get proper error messages
        try:
            with path.open(mode='r', encoding='utf-8') as file:
                data = _yml_setup.load(file)
            if data is None:
                data = {}
            set_parameter_file(path.stem, data)
        except Exception:
            log.error(f"Could not load params from {path.name}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'Loaded params from {path.name}!')


def unload_file(event: HABApp.core.events.habapp_events.RequestFileUnloadEvent):
    path = event.get_path(HABApp.CONFIG.directories.param)

    with LOCK:  # serialize to get proper error messages
        try:
            remove_parameter_file(path.stem)
        except Exception:
            log.error(f"Could not remove parameters from {path.name}!")
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.debug(f'Removed params from {path.name}!')


def save_file(file: str):
    assert isinstance(file, str), type(file)
    filename = HABApp.CONFIG.directories.param / (file + '.yml')

    with LOCK:  # serialize to get proper error messages
        log.info(f'Updated {filename}')
        with filename.open('w', encoding='utf-8') as outfile:
            _yml_setup.dump(get_parameter_file(file), outfile)
