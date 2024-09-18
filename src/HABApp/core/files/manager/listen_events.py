import logging

import HABApp
from HABApp.core.const.topics import TOPIC_FILES as T_FILES
from HABApp.core.events import EventFilter
from HABApp.core.events.habapp_events import RequestFileLoadEvent, RequestFileUnloadEvent
from HABApp.core.internals import EventBusListener, uses_event_bus, wrap_func


log = logging.getLogger('HABApp.Files')
event_bus = uses_event_bus()


async def _process_event(event: RequestFileUnloadEvent | RequestFileLoadEvent) -> None:
    name = event.name
    await HABApp.core.files.manager.process_file(name, HABApp.core.files.folders.get_path(name))


async def setup_file_manager() -> None:
    # Setup events so we can process load/unload
    event_bus.add_listener(
        EventBusListener(
            T_FILES, wrap_func(_process_event), EventFilter(RequestFileUnloadEvent)
        )
    )
    event_bus.add_listener(
        EventBusListener(
            T_FILES, wrap_func(_process_event), EventFilter(RequestFileLoadEvent)
        )
    )
