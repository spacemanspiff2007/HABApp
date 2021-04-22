import logging
from typing import Union

import HABApp
from HABApp.core.const.topics import FILES as T_FILES
from HABApp.core.events.habapp_events import RequestFileUnloadEvent, RequestFileLoadEvent

log = logging.getLogger('HABApp.Files')


async def _process_event(event: Union[RequestFileUnloadEvent, RequestFileLoadEvent]):
    name = event.name
    await HABApp.core.files.manager.process_file(name, HABApp.core.files.folders.get_path(name))


async def setup_file_manager():
    # Setup events so we can process load/unload
    HABApp.core.EventBus.add_listener(
        HABApp.core.EventBusListener(T_FILES, HABApp.core.WrappedFunction(_process_event), RequestFileUnloadEvent)
    )
    HABApp.core.EventBus.add_listener(
        HABApp.core.EventBusListener(T_FILES, HABApp.core.WrappedFunction(_process_event), RequestFileLoadEvent)
    )
