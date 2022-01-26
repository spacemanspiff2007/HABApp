import logging

import HABApp
from HABApp.core.base import EventBusBase, post_event
from HABApp.core.base import replace_dummy_objs

log = logging.getLogger('HABApp')


def create_event_bus() -> EventBusBase:
    from HABApp.core.event_bus import EventBus
    obj = EventBus()

    replace_dummy_objs(HABApp, post_event, obj.post_event)

    log.debug('Created event bus')
    return obj
