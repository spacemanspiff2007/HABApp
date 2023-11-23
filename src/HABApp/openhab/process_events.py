import logging
from typing import Union

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.asyncio import create_task_from_async
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.internals import uses_get_item, uses_post_event
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import process_exception
from HABApp.openhab.definitions.topics import TOPIC_ITEMS, TOPIC_THINGS
from HABApp.openhab.events import (
    GroupStateChangedEvent,
    GroupStateUpdatedEvent,
    ItemAddedEvent,
    ItemRemovedEvent,
    ItemUpdatedEvent,
    ThingAddedEvent,
    ThingConfigStatusInfoEvent,
    ThingRemovedEvent,
    ThingStatusInfoEvent,
    ThingUpdatedEvent,
)
from HABApp.openhab.item_to_reg import (
    add_thing_to_registry,
    add_to_registry,
    remove_from_registry,
    remove_thing_from_registry,
)
from HABApp.openhab.map_events import get_event


log = logging.getLogger('HABApp.openhab.items')

post_event = uses_post_event()
get_item = uses_get_item()


def on_sse_event(event_dict: dict, oh_3: bool):
    try:
        # Lookup corresponding OpenHAB event
        event = get_event(event_dict)

        # Update item in registry BEFORE posting to the event bus
        # so the items have the correct state when we process the event in a rule
        try:
            if isinstance(event, ValueUpdateEvent):
                __item = get_item(event.name)  # type: HABApp.core.items.base_valueitem.BaseValueItem
                __item.set_value(event.value)
                post_event(event.name, event)
                return None

            if isinstance(event, ValueChangeEvent):
                # Workaround because there is no GroupItemStateEvent in OH3
                if oh_3 and isinstance(event, GroupStateChangedEvent):
                    __item = get_item(event.name)  # type: HABApp.openhab.items.GroupItem
                    __item.set_value(event.value)
                    # Manually issue an GroupStateUpdatedEvent so we are consistent with OH4 behavior
                    post_event(event.name, GroupStateUpdatedEvent(event.name, event.item, event.value))
                post_event(event.name, event)
                return None

            if isinstance(event, (ThingStatusInfoEvent, ThingUpdatedEvent, ThingConfigStatusInfoEvent)):
                __thing = get_item(event.name)   # type: HABApp.openhab.items.Thing
                __thing.process_event(event)
                post_event(event.name, event)
                return None

        except ItemNotFoundException:
            log_warning(log, f'Received {event.__class__.__name__} for {event.name} but item does not exist!')

            # Post the event anyway
            post_event(event.name, event)
            return None

        # Events that add items to the item registry
        # These events require that we query openHAB because of the metadata, so we have to do it in a task
        if isinstance(event, (ItemAddedEvent, ItemUpdatedEvent)):
            create_task_from_async(item_event(event))
            return None

        # Events that remove items from the item registry
        if isinstance(event, ItemRemovedEvent):
            remove_from_registry(event.name)
            post_event(TOPIC_ITEMS, event)
            return None

        # Events that add things to the item registry
        if isinstance(event, ThingAddedEvent):
            add_thing_to_registry(event)
            post_event(TOPIC_THINGS, event)
            return None

        # Events that remove things from the item registry
        if isinstance(event, ThingRemovedEvent):
            remove_thing_from_registry(event.name)
            post_event(TOPIC_THINGS, event)
            return None

        # Unknown Event -> just forward it to the event bus
        post_event(event.name, event)
    except Exception as e:
        process_exception(func=on_sse_event, e=e)
        return None


async def item_event(event: Union[ItemAddedEvent, ItemUpdatedEvent]):
    try:
        from HABApp.openhab.map_items import map_item

        name = event.name

        # Since metadata is not part of the event we have to request it through the item
        if (cfg := await HABApp.openhab.interface_async.async_get_item(name)) is None:
            return None

        new_item = map_item(name, event.type, None, event.label, event.tags, event.groups, metadata=cfg.metadata)
        if new_item is None:
            return None

        add_to_registry(new_item)
        # Send Event to Event Bus
        post_event(TOPIC_ITEMS, event)
        return None
    except Exception as e:
        process_exception(func=item_event, e=e)
        return None
