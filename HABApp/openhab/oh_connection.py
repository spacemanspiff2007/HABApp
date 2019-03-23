import asyncio
import concurrent.futures
import itertools
import logging
import time
import traceback
import ujson

import aiohttp
from aiohttp_sse_client import client as sse_client

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.openhab.events import get_event
from HABApp.util import PrintException

from .connection import HttpConnection, HttpConnectionEventHandler

log = logging.getLogger('HABApp.openhab.Connection')
log_events = logging.getLogger('HABApp.Events.openhab')




class OpenhabConnection(HttpConnectionEventHandler):

    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime: HABApp.Runtime = parent

        self.connection = HttpConnection(self, self.runtime.config)

        self.__ping_sent = 0
        self.__ping_received = 0

        self.__tasks = []

        # Add the ping listener, this works because connect is the last step
        if self.runtime.config.openhab.ping.enabled:
            listener = HABApp.core.EventListener(
                self.runtime.config.openhab.ping.item,
                HABApp.core.WrappedFunction(self.ping_received),
                HABApp.openhab.events.ItemStateEvent
            )
            HABApp.core.Events.add_listener(listener)

        self.runtime.shutdown.register_func(self.shutdown)

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

        if not self.runtime.config.openhab.ping.enabled:
            return None

        log.debug('Started ping')
        while self.runtime.config.openhab.ping.enabled:
            asyncio.ensure_future(self.connection.async_post_update(
                self.runtime.config.openhab.ping.item,
                f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0'
            ))

            self.__ping_sent = time.time()
            await asyncio.sleep(10)



    def on_sse_event(self, event: dict):

        # Lookup corresponding OpenHAB event
        event = get_event(event)

        # log event
        if log_events.isEnabledFor(logging.DEBUG):
            log_events.log(logging.DEBUG, f'{event}')

        # Events which change the ItemRegistry
        if isinstance(event, (HABApp.openhab.events.ItemAddedEvent, HABApp.openhab.events.ItemUpdatedEvent)):
            item = HABApp.openhab.map_items(event.name, event.type, 'NULL')
            HABApp.core.Items.set_item(item)
        elif isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
            HABApp.core.Items.pop_item(event.name)

        # Send Event to Event Bus
        HABApp.core.Events.post_event(event.name, event)


    @PrintException
    async def update_all_items(self) -> int:

        try:
            data = await self.connection.async_get_items()

            found_items = len(data)
            for _dict in data:
                __item = HABApp.openhab.map_items(_dict['name'], _dict['type'], _dict['state'])
                HABApp.core.Items.set_item(__item)

            # remove items which are no longer available
            ist = set(HABApp.core.Items.items.keys())
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


    @PrintException
    def post_update(self, item, state):
        if not self.connection.is_online:
            return None

        asyncio.run_coroutine_threadsafe(
            self.connection.async_post_update(item, state),
            self.runtime.loop
        )

    @PrintException
    def send_command(self, item, state):
        if not self.connection.is_online:
            return None

        asyncio.run_coroutine_threadsafe(
            self.connection.async_send_command(item, state),
            self.runtime.loop
        )


    @PrintException
    def create_item(self, item_type, item_name, label="", category="", tags=[], groups=[]):
        if not self.connection.is_online:
            return None

        fut = asyncio.run_coroutine_threadsafe(
            self.connection.async_create_item(item_type, item_name, label, category, tags, groups),
            self.runtime.loop
        )
        return fut.result()

    @PrintException
    def remove_item(self, item_name):
        if not self.connection.is_online:
            return None

        fut = asyncio.run_coroutine_threadsafe(
            self.connection.async_remove_item(item_name),
            self.runtime.loop
        )
        return fut.result()
