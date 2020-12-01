from typing import Any, Callable, Optional
import logging
from pathlib import Path
from HABApp.core.logger import log_error

import HABApp


def add_event_bus_listener(
        file_type: str,
        func_load: Optional[Callable[[str, Path], Any]],
        func_unload: Optional[Callable[[str, Path], Any]],
        logger: logging.Logger):

    func = {
        'config': HABApp.core.files.file_name.is_config,
        'rule': HABApp.core.files.file_name.is_rule,
        'param': HABApp.core.files.file_name.is_param,
    }[file_type]

    def filter_func_load(event: HABApp.core.events.habapp_events.RequestFileLoadEvent):
        if not func(event.name):
            return None

        name = event.name
        path = event.get_path()

        # Only load existing files
        if not path.is_file():
            log_error(logger, f'{file_type} file "{path}" does not exist and can not be loaded!')
            return None

        func_load(name, path)

    def filter_func_unload(event: HABApp.core.events.habapp_events.RequestFileUnloadEvent):
        if not func(event.name):
            return None
        name = event.name
        path = event.get_path()
        func_unload(name, path)

    if filter_func_unload is not None:
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                HABApp.core.const.topics.FILES,
                HABApp.core.WrappedFunction(filter_func_unload),
                HABApp.core.events.habapp_events.RequestFileUnloadEvent
            )
        )

    if filter_func_load is not None:
        HABApp.core.EventBus.add_listener(
            HABApp.core.EventBusListener(
                HABApp.core.const.topics.FILES,
                HABApp.core.WrappedFunction(filter_func_load),
                HABApp.core.events.habapp_events.RequestFileLoadEvent
            )
        )
