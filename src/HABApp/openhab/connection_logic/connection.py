import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core import Items, EventBus
from HABApp.core.Items import ItemNotFoundException
from HABApp.core.logger import log_warning
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.connection_handler import http_connection
from HABApp.openhab.map_events import get_event
from HABApp.openhab.map_items import map_item
from ._plugin import on_connect, on_disconnect, setup_plugins

log = http_connection.log


def setup():
    from HABApp.runtime import shutdown

    # initialize callbacks
    http_connection.ON_CONNECTED = on_connect
    http_connection.ON_DISCONNECTED = on_disconnect
    http_connection.ON_SSE_EVENT = on_sse_event

    # shutdown handler for connection
    shutdown.register_func(http_connection.stop_connection, msg='Stopping openHAB connection')

    # shutdown handler for plugins
    shutdown.register_func(on_disconnect, msg='Stopping openHAB plugins')

    # initialize all plugins
    setup_plugins()
    return None


async def start():
    await http_connection.start_connection()


@ignore_exception
def on_sse_event(event_dict: dict):

    # Lookup corresponding OpenHAB event
    event = get_event(event_dict)

    # Update item in registry BEFORE posting to the event bus
    # so the items have the correct state when we process the event in a rule
    try:
        if isinstance(event, HABApp.core.events.ValueUpdateEvent):
            __item = Items.get_item(event.name)  # type: HABApp.core.items.base_item.BaseValueItem
            __item.set_value(event.value)
            EventBus.post_event(event.name, event)
            return None

        if isinstance(event, HABApp.openhab.events.ThingStatusInfoEvent):
            __thing = Items.get_item(event.name)   # type: HABApp.openhab.items.Thing
            __thing.process_event(event)
            EventBus.post_event(event.name, event)
            return None

        # Workaround because there is no GroupItemStateEvent
        if isinstance(event, HABApp.openhab.events.GroupItemStateChangedEvent):
            __item = Items.get_item(event.name)  # type: HABApp.openhab.items.GroupItem
            __item.set_value(event.value)
            EventBus.post_event(event.name, event)
            return None
    except ItemNotFoundException:
        log_warning(log, f'Received {event.__class__.__name__} for {event.name} but item does not exist!')

        # Post the event anyway
        EventBus.post_event(event.name, event)
        return None

    if isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
        Items.pop_item(event.name)
        EventBus.post_event(event.name, event)
        return None

    # Events which change the ItemRegistry
    new_item = None
    if isinstance(event, HABApp.openhab.events.ItemAddedEvent):
        new_item = map_item(event.name, event.type, None, event.tags, event.groups)
        if new_item is None:
            return None

    if isinstance(event, HABApp.openhab.events.ItemUpdatedEvent):
        new_item = map_item(event.name, event.type, None, event.tags, event.groups)
        if new_item is None:
            return None

    # check already existing item so we can print a warning if something changes
    if new_item is not None:
        try:
            existing_item = Items.get_item(new_item.name)
            if isinstance(existing_item, new_item.__class__):
                existing_item.tags = new_item.tags
                existing_item.groups = new_item.groups
                # it's the same item class so we don't replace it!
                new_item = existing_item
            else:
                log.warning(f'Item changed type from {existing_item.__class__} to {new_item.__class__}')
                # remove the item so it can be added again
                Items.pop_item(new_item.name)
        except Items.ItemNotFoundException:
            pass

        # always overwrite with new definition
        Items.add_item(new_item)

    # Send Event to Event Bus
    HABApp.core.EventBus.post_event(event.name, event)
    return None
