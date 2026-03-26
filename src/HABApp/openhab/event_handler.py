import logging
from typing import Final

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.asyncio import create_task_from_async
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.logger import log_warning
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.core.wrapper import process_exception
from HABApp.openhab.definitions.topics import TOPIC_ITEMS, TOPIC_THINGS
from HABApp.openhab.events import (
    ItemAddedEvent,
    ItemRemovedEvent,
    ItemUpdatedEvent,
    OpenhabEvent,
    ThingAddedEvent,
    ThingConfigStatusInfoEvent,
    ThingRemovedEvent,
    ThingStatusInfoEvent,
    ThingUpdatedEvent,
)
from HABApp.openhab.item_factory import OhItemFactory
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler


log = logging.getLogger('HABApp.openhab.items')


@HABAPP_PROVIDER.register
class OhEventHandler:
    __slots__ = ('_event_bus', '_item_factory', '_item_registry', '_registry_handler')

    def __init__(self, event: EventBus, item_registry: ItemRegistry,
                 registry_handler: OhItemRegistryHandler, item_factory: OhItemFactory) -> None:

        self._event_bus: Final = event
        self._registry_handler: Final = registry_handler
        self._item_registry: Final = item_registry
        self._item_factory: Final = item_factory

    def on_openhab_event(self, event: OpenhabEvent) -> None:
        post_event: Final = self._event_bus.post_event

        try:
            # Update item in registry BEFORE posting to the event bus
            # so the items have the correct state when we process the event in a rule
            try:
                if isinstance(event, ValueUpdateEvent):
                    __item = self._item_registry.get_item(event.name)  # type: HABApp.core.items.base_valueitem.BaseValueItem
                    __item.set_value(event.value)
                    post_event(event.name, event)
                    return None

                if isinstance(event, ValueChangeEvent):
                    post_event(event.name, event)
                    return None

                if isinstance(event, (ThingStatusInfoEvent, ThingUpdatedEvent, ThingConfigStatusInfoEvent)):
                    __thing = self._item_registry.get_item(event.name)   # type: HABApp.openhab.items.Thing
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
                create_task_from_async(self.item_event(event))
                return None

            # Events that remove items from the item registry
            if isinstance(event, ItemRemovedEvent):
                self._registry_handler.remove_from_registry(event.name)
                post_event(TOPIC_ITEMS, event)
                return None

            # Events that add things to the item registry
            if isinstance(event, ThingAddedEvent):
                self._registry_handler.add_thing_to_registry(event)
                post_event(TOPIC_THINGS, event)
                return None

            # Events that remove things from the item registry
            if isinstance(event, ThingRemovedEvent):
                self._registry_handler.remove_thing_from_registry(event.name)
                post_event(TOPIC_THINGS, event)
                return None

            # Unknown Event -> just forward it to the event bus
            post_event(event.name, event)
        except Exception as e:
            process_exception(func=self.on_openhab_event, e=e)
            return None

    async def item_event(self, event: ItemAddedEvent | ItemUpdatedEvent) -> None:
        try:

            name = event.name

            # Since metadata is not part of the event we have to request it through the item
            if (cfg := await HABApp.openhab.interface_async.async_get_item(name)) is None:
                return None

            new_item = self._item_factory.create_item(
                name, event.type, value=None, last_value=None,
                label=event.label, tags=event.tags, groups=event.groups, metadata=cfg.metadata
            )
            if new_item is None:
                return None

            self._registry_handler.add_to_registry(new_item)
            # Send Event to Event Bus
            self._event_bus.post_event(TOPIC_ITEMS, event)

        except Exception as e:
            process_exception(func=self.item_event, e=e)

        return None
