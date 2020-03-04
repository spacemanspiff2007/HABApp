import asyncio
import logging
import time

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.openhab.map_events import get_event
from HABApp.core.wrapper import log_exception, ignore_exception
from .http_connection import HttpConnection, HttpConnectionEventHandler
from .oh_interface import get_openhab_interface
from ..config import Openhab as OpenhabConfig

log = logging.getLogger('HABApp.openhab.Connection')


class OpenhabConnection(HttpConnectionEventHandler):

    def __init__(self, config: OpenhabConfig, shutdown):
        assert isinstance(config, OpenhabConfig), type(config)
        assert isinstance(shutdown, HABApp.runtime.ShutdownHelper), type(shutdown)

        self.config = config

        self.connection = HttpConnection(self, self.config)
        self.interface = get_openhab_interface(self.connection)

        self.__ping_sent = 0
        self.__ping_received = 0

        # Add the ping listener, this works because connect is the last step
        if self.config.ping.enabled:
            listener = HABApp.core.EventBusListener(
                self.config.ping.item,
                HABApp.core.WrappedFunction(self.ping_received),
                HABApp.openhab.events.ItemStateEvent
            )
            HABApp.core.EventBus.add_listener(listener)

        shutdown.register_func(self.shutdown)

        # todo: currently this does not work
        # # reload config
        # HABApp.CONFIG.openhab.connection.subscribe_for_changes(
        #     lambda : asyncio.run_coroutine_threadsafe(self.__create_session(), self.runtime.loop).result()
        # )

        self.__async_sse: asyncio.Future = None
        self.__async_items: asyncio.Future = None
        self.__async_ping: asyncio.Future = None

    def on_connected(self):
        # Start SSE Processing
        self.__async_sse = asyncio.ensure_future(self.connection.async_process_sse_events())

        # Read all Items
        self.__async_items = asyncio.ensure_future(self.update_all_items())

        # start ping
        self.__async_ping = asyncio.ensure_future(self.async_ping())

    @log_exception
    def on_disconnected(self):

        for future in (self.__async_sse, self.__async_items, self.__async_ping):
            if future is None:
                continue
            # if it is still running cancel
            if not future.done():
                future.cancel()

    async def start(self):
        await self.connection.try_connect()

    @log_exception
    def shutdown(self):
        self.on_disconnected()
        self.connection.cancel_connect()

    def ping_received(self, event):
        self.__ping_received = time.time()

    @log_exception
    async def async_ping(self):

        if not self.config.ping.enabled:
            return None

        log.debug('Started ping')
        while self.config.ping.enabled:
            self.interface.post_update(
                self.config.ping.item,
                f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0'
            )

            self.__ping_sent = time.time()
            await asyncio.sleep(self.config.ping.interval)

    @ignore_exception
    def on_sse_event(self, event_dict: dict):

        # Lookup corresponding OpenHAB event
        event = get_event(event_dict)

        # Update item in registry BEFORE posting to the event bus
        # so the items have the correct state when we process the event in a rule
        try:
            if isinstance(event, HABApp.core.events.ValueUpdateEvent):
                __item = HABApp.core.Items.get_item(event.name)  # type: HABApp.core.items.base_item.BaseValueItem
                __item.set_value(event.value)
                HABApp.core.EventBus.post_event(event.name, event)
                return None
            elif isinstance(event, HABApp.openhab.events.ThingStatusInfoEvent):
                __thing = HABApp.core.Items.get_item(event.name)   # type: HABApp.openhab.items.Thing
                __thing.process_event(event)
                HABApp.core.EventBus.post_event(event.name, event)
                return None
        except HABApp.core.Items.ItemNotFoundException:
            pass

        # Events which change the ItemRegistry
        if isinstance(event, (HABApp.openhab.events.ItemAddedEvent, HABApp.openhab.events.ItemUpdatedEvent)):
            item = HABApp.openhab.map_items(event.name, event.type, 'NULL')

            # check already existing item so we can print a warning if something changes
            try:
                existing_item = HABApp.core.Items.get_item(item.name)
                if isinstance(existing_item, item.__class__):
                    # it's the same item class so we don't replace it!
                    item = existing_item
                else:
                    log.warning(f'Item changed type from {existing_item.__class__} to {item.__class__}')
            except HABApp.core.Items.ItemNotFoundException:
                pass

            # always overwrite with new definition
            HABApp.core.Items.set_item(item)

        elif isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
            HABApp.core.Items.pop_item(event.name)

        # Send Event to Event Bus
        HABApp.core.EventBus.post_event(event.name, event)
        return None

    @ignore_exception
    async def update_all_items(self):
        data = await self.connection.async_get_items()
        if data is None:
            return None

        found_items = len(data)
        for _dict in data:
            item_name = _dict['name']
            new_item = HABApp.openhab.map_items(item_name, _dict['type'], _dict['state'])

            try:
                # if the item already exists and it has the correct type just update its state
                # Since we load the items before we load the rules this should actually never happen
                existing_item = HABApp.core.Items.get_item(item_name)
                if isinstance(existing_item, new_item.__class__):
                    existing_item.set_value(new_item.value)  # use the converted state from the new item here
                    new_item = existing_item
            except HABApp.core.Items.ItemNotFoundException:
                pass

            # create new item or change item type
            HABApp.core.Items.set_item(new_item)

        # remove items which are no longer available
        ist = set(HABApp.core.Items.get_all_item_names())
        soll = {k['name'] for k in data}
        for k in ist - soll:
            if isinstance(HABApp.core.Items.get_item(k), HABApp.openhab.items.OpenhabItem):
                HABApp.core.Items.pop_item(k)

        log.info(f'Updated {found_items:d} Items')


        # try to update things, too
        data = await self.connection.async_get_things()
        if data is None:
            return None

        Thing = HABApp.openhab.items.Thing
        for t_dict in data:
            name = t_dict['UID']
            try:
                thing = HABApp.core.Items.get_item(name)
                if not isinstance(thing, Thing):
                    log.warning(f'Item {name} has the wrong type ({type(thing)}), expected Thing')
                    thing = Thing(name)
            except HABApp.core.Items.ItemNotFoundException:
                thing = Thing(name)

            thing.status = t_dict['statusInfo']['status']
            HABApp.core.Items.set_item(thing)

        # remove things which were deleted
        ist = set(HABApp.core.Items.get_all_item_names())
        soll = {k['UID'] for k in data}
        for k in ist - soll:
            if isinstance(HABApp.core.Items.get_item(k), Thing):
                HABApp.core.Items.pop_item(k)

        log.info(f'Updated {len(data):d} Things')

        return None
