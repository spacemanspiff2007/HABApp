import asyncio
import logging
import time
import traceback

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.openhab.events import get_event
from HABApp.util import PrintException
from .http_connection import HttpConnection, HttpConnectionEventHandler
from .oh_interface import get_openhab_interface

log = logging.getLogger('HABApp.openhab.Connection')



class OpenhabConnection(HttpConnectionEventHandler):

    def __init__(self, config, shutdown):
        assert isinstance(config, HABApp.config.Config), type(config)
        assert isinstance(shutdown, HABApp.runtime.ShutdownHelper), type(shutdown)

        self.config = config

        self.connection = HttpConnection(self, self.config)
        self.interface = get_openhab_interface(self.connection)

        self.__ping_sent = 0
        self.__ping_received = 0

        # Add the ping listener, this works because connect is the last step
        if self.config.openhab.ping.enabled:
            listener = HABApp.core.EventBusListener(
                self.config.openhab.ping.item,
                HABApp.core.WrappedFunction(self.ping_received),
                HABApp.openhab.events.ItemStateEvent
            )
            HABApp.core.EventBus.add_listener(listener)

        shutdown.register_func(self.shutdown)

        # todo: currently this does not work
        # # reload config
        # self.runtime.config.openhab.connection.subscribe_for_changes(
        #     lambda : asyncio.run_coroutine_threadsafe(self.__create_session(), self.runtime.loop).result()
        # )

        self.__async_sse: asyncio.Future = None
        self.__async_items: asyncio.Future = None

    def on_connected(self):
        # Start SSE Processing
        self.__async_sse = asyncio.ensure_future(self.connection.async_process_sse_events())

        # Read all Items
        self.__async_items = asyncio.ensure_future(self.update_all_items())


    def on_disconnected(self):
        if self.__async_sse:
            if not self.__async_sse.done():
                self.__async_sse.cancel()

        if self.__async_items:
            if not self.__async_items.done():
                self.__async_items.cancel()

    async def start(self):
        await self.connection.try_connect()

    def shutdown(self):
        self.on_disconnected()
        self.connection.cancel_connect()

    @PrintException
    def ping_received(self, event):
        self.__ping_received = time.time()

    @PrintException
    async def async_ping(self):

        if not self.config.openhab.ping.enabled:
            return None

        log.debug('Started ping')
        while self.config.openhab.ping.enabled:
            self.interface.post_update(
                self.config.openhab.ping.item,
                f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0'
            )

            self.__ping_sent = time.time()
            await asyncio.sleep(10)



    def on_sse_event(self, event: dict):

        try:
            # Lookup corresponding OpenHAB event
            event = get_event(event)

            # Events which change the ItemRegistry
            if isinstance(event, (HABApp.openhab.events.ItemAddedEvent, HABApp.openhab.events.ItemUpdatedEvent)):
                item = HABApp.openhab.map_items(event.name, event.type, 'NULL')
                try:
                    existing_item = HABApp.core.Items.get_item(item.name)
                    if not isinstance(existing_item, item.__class__):
                        log.warning( f'Item changed type from {existing_item.__class__} to {item.__class__}')
                except HABApp.core.Items.ItemNotFoundException:
                    HABApp.core.Items.set_item(item)

            elif isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
                HABApp.core.Items.pop_item(event.name)

            # Update Item in registry BEFORE posting to the event bus
            if isinstance(event, HABApp.core.events.ValueUpdateEvent):
                try:
                    HABApp.core.Items.get_item(event.name).set_state(event.value)
                except HABApp.core.Items.ItemNotFoundException:
                    pass

            # Send Event to Event Bus
            HABApp.core.EventBus.post_event(event.name, event)

        except Exception as e:
            log.error(e)
            for line in traceback.format_exc().splitlines():
                log.error(line)


    @PrintException
    async def update_all_items(self) -> int:

        try:
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
                        existing_item.set_state(_dict['state'])
                except HABApp.core.Items.ItemNotFoundException:
                    pass

                # create new item or change item type
                HABApp.core.Items.set_item(new_item)

            # remove items which are no longer available
            ist = set(HABApp.core.Items.get_item_names())
            soll = {k['name'] for k in data}
            for k in ist - soll:
                HABApp.core.Items.pop_item(k)

            log.info(f'Updated {found_items:d} items')
            return found_items
        except Exception as e:
            log.error(e)
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return 0
