from asyncio import create_task
from typing import Union

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.internals import uses_get_item, uses_post_event
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import process_exception
from HABApp.openhab.connection_handler import http_connection
from HABApp.openhab.definitions.topics import ITEMS as ITEMS_TOPIC
from HABApp.openhab.events import GroupItemStateChangedEvent, ItemAddedEvent, \
    ItemCommandEvent, ItemRemovedEvent, ItemUpdatedEvent, ThingStatusInfoEvent
from HABApp.openhab.item_to_reg import add_to_registry, remove_from_registry
from HABApp.openhab.map_events import get_event
from HABApp.openhab.map_items import map_item

log = http_connection.log


post_event = uses_post_event()
get_item = uses_get_item()


def on_sse_event(event_dict: dict):
    try:
        # Lookup corresponding OpenHAB event
        event = get_event(event_dict)

        # Update item in registry BEFORE posting to the event bus
        # so the items have the correct state when we process the event in a rule
        try:
            if isinstance(event, ItemCommandEvent) or \
               isinstance(event, ValueChangeEvent) or \
               isinstance(event, ValueUpdateEvent):
                __item = get_item(event.name)  # type: HABApp.core.items.base_item.BaseValueItem
                __item.set_value(event.value)
                post_event(event.name, event)
                return None

            if isinstance(event, ThingStatusInfoEvent):
                __thing = get_item(event.name)   # type: HABApp.openhab.items.Thing
                __thing.process_event(event)
                post_event(event.name, event)
                return None

            # Workaround because there is no GroupItemStateEvent
            if isinstance(event, GroupItemStateChangedEvent):
                __item = get_item(event.name)  # type: HABApp.openhab.items.GroupItem
                __item.set_value(event.value)
                post_event(event.name, event)
                return None
        except ItemNotFoundException:
            log_warning(log, f'Received {event.__class__.__name__} for {event.name} but item does not exist!')

            # Post the event anyway
            post_event(event.name, event)
            return None

        # Events that remove items from the item registry
        if isinstance(event, ItemRemovedEvent):
            remove_from_registry(event.name)
            post_event(ITEMS_TOPIC, event)
            return None

        # Events that add items to the item registry
        # These events require that we query openHAB because of the metadata so we have to do it in a task
        if isinstance(event, (ItemAddedEvent, ItemUpdatedEvent)):
            create_task(item_event(event))
            return None

        # Unknown Event -> just forward it to the event bus
        post_event(event.name, event)
    except Exception as e:
        process_exception(func=on_sse_event, e=e)
        return None


async def item_event(event: Union[ItemAddedEvent, ItemUpdatedEvent]):
    name = event.name

    # Since metadata is not part of the event we have to request it
    cfg = await HABApp.openhab.interface_async.async_get_item(name, metadata='.+')

    new_item = map_item(name, event.type, None, event.tags, event.groups, metadata=cfg.get('metadata'))
    if new_item is None:
        return None

    add_to_registry(new_item)
    # Send Event to Event Bus
    post_event(ITEMS_TOPIC, event)
    return None
