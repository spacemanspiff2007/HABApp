import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core import Items
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.connection_handler import http_connection
from HABApp.openhab.map_events import get_event
from HABApp.openhab.map_items import map_item
from ._plugin import on_connect, on_disconnect, setup_plugins

log = http_connection.log


def setup(shutdown):
    assert isinstance(shutdown, HABApp.runtime.ShutdownHelper), type(shutdown)

    # initialize callbacks
    http_connection.ON_CONNECTED = on_connect
    http_connection.ON_DISCONNECTED = on_disconnect
    http_connection.ON_SSE_EVENT = on_sse_event

    # shutdown handler for connection
    shutdown.register_func(http_connection.stop_connection)

    # shutdown handler for plugins
    shutdown.register_func(on_disconnect)

    # initialize all plugins
    setup_plugins()
    return None


async def start():
    await http_connection.start_connection(),


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
            HABApp.core.EventBus.post_event(event.name, event)
            return None
        elif isinstance(event, HABApp.openhab.events.ThingStatusInfoEvent):
            __thing = Items.get_item(event.name)   # type: HABApp.openhab.items.Thing
            __thing.process_event(event)
            HABApp.core.EventBus.post_event(event.name, event)
            return None
    except HABApp.core.Items.ItemNotFoundException:
        pass

    # Events which change the ItemRegistry
    if isinstance(event, (HABApp.openhab.events.ItemAddedEvent, HABApp.openhab.events.ItemUpdatedEvent)):
        item = map_item(event.name, event.type, 'NULL')
        if item is None:
            return None

        # check already existing item so we can print a warning if something changes
        try:
            existing_item = Items.get_item(item.name)
            if isinstance(existing_item, item.__class__):
                # it's the same item class so we don't replace it!
                item = existing_item
            else:
                log.warning(f'Item changed type from {existing_item.__class__} to {item.__class__}')
                # remove the item so it can be added again
                Items.pop_item(item.name)
        except Items.ItemNotFoundException:
            pass

        # always overwrite with new definition
        Items.add_item(item)

    elif isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
        Items.pop_item(event.name)

    # Send Event to Event Bus
    HABApp.core.EventBus.post_event(event.name, event)
    return None
