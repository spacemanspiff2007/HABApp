import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core import Items, EventBus
from HABApp.core.Items import ItemNotFoundException
from HABApp.core.events import ValueUpdateEvent
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.connection_handler import http_connection
from HABApp.openhab.events import ThingStatusInfoEvent, GroupItemStateChangedEvent, ItemRemovedEvent, ItemAddedEvent, \
    ItemUpdatedEvent
from HABApp.openhab.map_events import get_event
from HABApp.openhab.map_items import map_item
from HABApp.openhab.item_to_reg import add_item_to_registry


log = http_connection.log


@ignore_exception
def on_sse_event(event_dict: dict):

    # Lookup corresponding OpenHAB event
    event = get_event(event_dict)

    # Update item in registry BEFORE posting to the event bus
    # so the items have the correct state when we process the event in a rule
    try:
        if isinstance(event, ValueUpdateEvent):
            __item = Items.get_item(event.name)  # type: HABApp.core.items.base_item.BaseValueItem
            __item.set_value(event.value)
            EventBus.post_event(event.name, event)
            return None

        if isinstance(event, ThingStatusInfoEvent):
            __thing = Items.get_item(event.name)   # type: HABApp.openhab.items.Thing
            __thing.process_event(event)
            EventBus.post_event(event.name, event)
            return None

        # Workaround because there is no GroupItemStateEvent
        if isinstance(event, GroupItemStateChangedEvent):
            __item = Items.get_item(event.name)  # type: HABApp.openhab.items.GroupItem
            __item.set_value(event.value)
            EventBus.post_event(event.name, event)
            return None
    except ItemNotFoundException:
        log_warning(log, f'Received {event.__class__.__name__} for {event.name} but item does not exist!')

        # Post the event anyway
        EventBus.post_event(event.name, event)
        return None

    if isinstance(event, ItemRemovedEvent):
        Items.pop_item(event.name)
        EventBus.post_event(event.name, event)
        return None

    # Events which change the ItemRegistry
    new_item = None
    if isinstance(event, ItemAddedEvent):
        new_item = map_item(event.name, event.type, None, event.tags, event.groups)
        if new_item is None:
            return None

    if isinstance(event, ItemUpdatedEvent):
        new_item = map_item(event.name, event.type, None, event.tags, event.groups)
        if new_item is None:
            return None

    if new_item is not None:
        add_item_to_registry(new_item)

    # Send Event to Event Bus
    HABApp.core.EventBus.post_event(event.name, event)
    return None
