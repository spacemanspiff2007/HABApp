import asyncio
import logging
import time

import aiohttp, ujson, itertools
from aiohttp_sse_client import client as sse_client

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.util import PrintException

log = logging.getLogger('HABApp.Core.Connection')

class Connection:
    def __init__(self, parent):
        assert isinstance(parent, HABApp.Runtime)
        self.runtime : HABApp.Runtime = parent

        self.__session : aiohttp.ClientSession = None

        self.queue_send_command = asyncio.Queue()
        self.queue_post_update  = asyncio.Queue()

        self.__host = self.runtime.config.connection['host']
        self.__port = self.runtime.config.connection['port']

        self.__ping_sent = 0
        self.__ping_received  = 0

        self.__tasks = []

        #Add the ping listener, this works because connect is the last step
        listener = HABApp.core.EventBusListener( self.runtime.config.ping_item, self.ping_received, HABApp.openhab.events.ItemStateEvent)
        self.runtime.events.add_listener(listener)

        self.runtime.shutdown.register_func(self.shutdown)

    def __get_url(self, url : str):
        r = f'http://{self.__host:s}:{self.__port:d}'
        return r + url if url.startswith('/') else r + '/' + url

    def shutdown(self):
        for k in self.__tasks:
            k.cancel()

    @PrintException
    def get_async(self):

        self.__tasks = [
            asyncio.ensure_future(self.async_listen_for_sse_events()),
            asyncio.ensure_future(self.async_ping()),
            asyncio.ensure_future(self.async_post_update()),
            asyncio.ensure_future(self.async_send_command()),
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
        log.debug('Started ping')

        while self.runtime.config.ping_enabled:
            self.queue_post_update.put_nowait(
                (self.runtime.config.ping_item,
                 f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0')
            )
            self.__ping_sent = time.time()
            await asyncio.sleep(10)

    @PrintException
    async def async_listen_for_sse_events(self):
        "This is the worker thread who creates the connection"

        auth = None
        if self.runtime.config.connection['user'] or self.runtime.config.connection['pass']:
            auth = aiohttp.BasicAuth(
                self.runtime.config.connection['user'],
                self.runtime.config.connection['pass']
            )

        self.__session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=99999999999999999),
            json_serialize = ujson.dumps,
            auth=auth
        )

        log.debug('Started SSE listener')
        while not self.runtime.shutdown.requested:
            try:
                async with sse_client.EventSource( self.__get_url("/rest/events?topics=smarthome/items/"), session=self.__session) as event_source:
                    async for event in event_source:
                        self.runtime.events.post_event(event.data)
            except Exception as e:
                if isinstance(e, aiohttp.ClientPayloadError) or isinstance(e, ConnectionError) or isinstance(e, aiohttp.ClientConnectorError):
                    log.warning(f'SSE request Error: {e}')
                else:
                    log.error(f'SSE request Error: {e}')
                    raise

            await asyncio.sleep(3)

        #close session
        await self.__session.close()
        return None

    @PrintException
    async def async_get_all_items(self):

        # we need to wait so the session object is available
        await asyncio.sleep(1)

        while True:
            try:
                resp = await self.__session.get(self.__get_url('rest/items'), params={'recursive' : 'false', 'fields' : 'state,type,name,editable'})
                if resp.status == 200:
                    data = await resp.text()
                    self.runtime.all_items.set_items(data)
                    break
            except Exception as e:
                if isinstance(e, aiohttp.ClientPayloadError) or isinstance(e, ConnectionError) or isinstance(e, aiohttp.ClientConnectorError):
                    log.warning(f'SSE request Error: {e}')
                else:
                    log.error(f'SSE request Error: {e}')
                    raise

            await asyncio.sleep(3)

    @PrintException
    async def __check_request_result( self, future, data=None):

        try:
            resp = await future
            #print(resp.request_info)
        except Exception as e:
            if isinstance(e, aiohttp.ClientPayloadError) or isinstance(e, ConnectionError) or isinstance(e, aiohttp.ClientConnectorError):
                log.warning(e)
                return None
            raise

        #IO -> Quit
        if resp.status >= 300:
            #Log Error Message
            msg = f'Status {resp.status} for {resp.request_info.method} {resp.request_info.url}'
            if data:
                msg += f' {data}'
            log.warning(msg)
            for line in str(resp).splitlines():
                log.warning(line)

        return resp.status


    @PrintException
    async def async_post_update(self):
        log.debug('Started postUpdate worker')
        url = self.__get_url('rest/items')
        await asyncio.sleep(1)

        while True:
            item, state = await self.queue_post_update.get()
            self.queue_post_update.task_done()

            fut = self.__session.put(f'{url:s}/{item}/state', data=state)
            asyncio.ensure_future( self.__check_request_result(fut, state))

            #asyncio.ensure_future(self.__check_outgoing_comm(self.__session, 'put',f'{url:s}/{item}/state', state))

    @PrintException
    async def async_send_command(self):
        log.debug('Started sendCommand worker')
        url = self.__get_url('rest/items')
        await asyncio.sleep(1)

        while True:
            item, state = await self.queue_send_command.get()
            self.queue_send_command.task_done()

            fut = self.__session.post(f'{url:s}/{item}', data=state)
            asyncio.ensure_future( self.__check_request_result(fut, state))


    @PrintException
    async def async_create_item(self, item_type, item_name, label = "", category = "", tags = [], groups = []):

        payload = {'type' : item_type, 'name' : item_name}
        if label:
            payload['label'] = label
        if label:
            payload['category'] = category
        if label:
            payload['tags'] = tags
        if label:
            payload['groupnames'] = groups

        fut = self.__session.put(self.__get_url(f'rest/items/{item_name}'), json=payload)
        ret = await self.__check_request_result(fut, payload)
        return ret == 200 or ret == 201

    @PrintException
    async def async_remove_item(self, item_name):

        fut = self.__session.delete(self.__get_url(f'rest/items/{item_name}'))
        ret = await self.__check_request_result(fut)
        return ret == 200 or ret == 201