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

log = logging.getLogger('HABApp.openhab.Connection')
log_events = logging.getLogger('HABApp.Events.openhab')

def is_ignored_exception(e) -> bool:
    if isinstance(e, aiohttp.ClientPayloadError) or \
            isinstance(e, ConnectionError) or \
            isinstance(e, aiohttp.ClientConnectorError) or \
            isinstance(e, concurrent.futures._base.CancelledError):  # kommt wenn wir einen task canceln
        return True
    return False


class Connection:

    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime: HABApp.Runtime = parent

        self.__session: aiohttp.ClientSession = None

        self.__host: str = ''
        self.__port: str = ''

        self.__ping_sent = 0
        self.__ping_received = 0

        self.__tasks = []

        # Add the ping listener, this works because connect is the last step
        if self.runtime.config.openhab.ping.enabled:
            listener = HABApp.core.EventListener(
                self.runtime.config.openhab.ping.item,
                self.ping_received,
                HABApp.openhab.events.ItemStateEvent
            )
            HABApp.core.Events.add_listener(listener)

        self.runtime.shutdown.register_func(self.shutdown)

        # todo: currently this does not work
        # # reload config
        # self.runtime.config.openhab.connection.subscribe_for_changes(
        #     lambda : asyncio.run_coroutine_threadsafe(self.__create_session(), self.runtime.loop).result()
        # )

    def __get_url(self, url: str, *args, **kwargs):

        prefix = f'http://{self.__host:s}:{self.__port:d}{ "" if url.startswith("/") else "/":s}'
        url = url.format(*args, **kwargs)
        return prefix + url

    def shutdown(self):
        for k in self.__tasks:
            k.cancel()

    @PrintException
    def get_async(self):

        # These Tasks run in the Background and have to be canceled on shutdown
        self.__tasks = [
            asyncio.ensure_future(self.async_listen_for_sse_events()),
            asyncio.ensure_future(self.async_ping()),
        ]

        return asyncio.gather(
            *itertools.chain(
                self.__tasks,
                [asyncio.ensure_future(self.async_get_all_items())]
            )
        )

    @PrintException
    def ping_received(self, event):
        self.__ping_received = time.time()

    @PrintException
    async def async_ping(self):
        # we need to wait so the session object is available
        await asyncio.sleep(1)
        if self.__session is None:
            return None

        log.debug('Started ping')
        while self.runtime.config.openhab.ping.enabled:

            await self.async_post_update(
                self.runtime.config.openhab.ping.item,
                f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0'
            )
            self.__ping_sent = time.time()
            await asyncio.sleep(10)

    async def __create_session(self):

        # If we are already connected properly disconnect
        if self.__session is not None:
            await self.__session.close()
            self.__session = None

        self.__host: str = self.runtime.config.openhab.connection.host
        self.__port: str = self.runtime.config.openhab.connection.port

        # do not run without host
        if self.__host == '':
            return None

        auth = None
        if self.runtime.config.openhab.connection.user or self.runtime.config.openhab.connection.password:
            auth = aiohttp.BasicAuth(
                self.runtime.config.openhab.connection.user,
                self.runtime.config.openhab.connection.password
            )

        self.__session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=99999999999999999),
            json_serialize=ujson.dumps,
            auth=auth
        )

    @PrintException
    async def async_listen_for_sse_events(self):
        "This is the worker thread who creates the connection"

        await self.__create_session()
        if self.__host is None:
            log.info('OpenHAB disabled')
            return None

        log.debug('Started SSE listener')
        while not self.runtime.shutdown.requested:
            try:
                async with sse_client.EventSource(
                        self.__get_url("/rest/events?topics=smarthome/items/"),
                        session=self.__session
                ) as event_source:
                    async for event in event_source:
                        try:
                            event = ujson.loads(event.data)
                            if log_events.isEnabledFor(logging.DEBUG):
                                log_events._log(logging.DEBUG, event, [])
                            event = get_event(event)
                            
                            if isinstance(event, HABApp.openhab.events.ItemAddedEvent) or \
                                    isinstance(event, HABApp.openhab.events.ItemUpdatedEvent):
                                item = HABApp.openhab.map_items( event.name, event.type, 'NULL')
                                HABApp.core.Items.set_item(item)
                            elif isinstance(event, HABApp.openhab.events.ItemRemovedEvent):
                                HABApp.core.Items.pop_item(event.name)
                            
                            HABApp.core.Events.post_event( event.name, event)
                            
                        except Exception as e:
                            log.error("{}".format(e))
                            for l in traceback.format_exc().splitlines():
                                log.error(l)
                            return None

            except Exception as e:
                lvl = logging.WARNING if is_ignored_exception(e) else logging.ERROR
                log.log(lvl, f'SSE request Error: {e}')
                for l in traceback.format_exc().splitlines():
                    log.log(lvl, l)
                if lvl == logging.ERROR:
                    raise

            await asyncio.sleep(3)

        # close session
        await self.__session.close()
        return None

    @PrintException
    def __update_all_items(self, data):
            data = ujson.loads(data)  # type: list
            for _dict in data:
                __item = HABApp.openhab.map_items(_dict['name'], _dict['type'], _dict['state'])
                HABApp.core.Items.set_item(__item)

            # remove items which are no longer available
            ist = set(HABApp.core.Items.items.keys())
            soll = {k['name'] for k in data}
            for k in ist - soll:
                HABApp.core.Items.pop_item(k)

            log.info(f'Updated all items')

    @PrintException
    async def async_get_all_items(self):

        # we need to wait so the session object is available
        await asyncio.sleep(1)
        if self.__session is None:
            return None

        while True:
            try:
                resp = await self.__session.get(
                    self.__get_url('rest/items'),
                    json={'recursive': 'false', 'fields': 'state,type,name,editable'}
                )
                if resp.status == 200:
                    data = await resp.text()
                    self.__update_all_items(data)
                    break
            except Exception as e:
                if is_ignored_exception(e):
                    log.warning(f'SSE request Error: {e}')
                else:
                    log.error(f'SSE request Error: {e}')
                    raise

            await asyncio.sleep(3)

    @PrintException
    async def __check_request_result(self, future, data=None):

        try:
            resp = await future
            # print(resp.request_info)
        except Exception as e:
            if is_ignored_exception(e):
                log.warning(e)
                return None
            raise

        # IO -> Quit
        if resp.status >= 300:
            # Log Error Message
            msg = f'Status {resp.status} for {resp.request_info.method} {resp.request_info.url}'
            if data:
                msg += f' {data}'
            log.warning(msg)
            for line in str(resp).splitlines():
                log.warning(line)

        return resp.status

    @PrintException
    async def async_post_update(self, item, state):

        fut = self.__session.put(self.__get_url('rest/items/{item:s}/state', item=item), data=state)
        asyncio.ensure_future(self.__check_request_result(fut, state))

    @PrintException
    async def async_send_command(self, item, state):

        fut = self.__session.post(self.__get_url('rest/items/{item:s}', item=item), data=state)
        asyncio.ensure_future(self.__check_request_result(fut, state))


    @PrintException
    async def async_create_item(self, item_type, item_name, label="", category="", tags=[], groups=[]):

        payload = {'type': item_type, 'name': item_name}
        if label:
            payload['label'] = label
        if label:
            payload['category'] = category
        if label:
            payload['tags'] = tags
        if label:
            payload['groupnames'] = groups

        fut = self.__session.put(self.__get_url('rest/items/{:s}', item_name), json=payload)
        ret = await self.__check_request_result(fut, payload)
        return ret == 200 or ret == 201

    @PrintException
    async def async_remove_item(self, item_name):

        fut = self.__session.delete(self.__get_url('rest/items/{:s}', item_name))
        ret = await self.__check_request_result(fut)
        return ret == 200 or ret == 201
