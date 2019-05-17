import asyncio
import logging
import traceback
import typing

import aiohttp
import ujson
from aiohttp.client import ClientResponse
from aiohttp_sse_client import client as sse_client

import HABApp
import HABApp.core
import HABApp.openhab.events

log = logging.getLogger('HABApp.openhab.connection')
log_events = logging.getLogger('HABApp.Events.openhab')


class OpenhabDisconnectedError(Exception):
    pass


class OpenhabNotReadyYet(Exception):
    pass


class HttpConnectionEventHandler:
    def on_connected(self):
        raise NotImplementedError()

    def on_disconnected(self):
        raise NotImplementedError()

    def on_sse_event(self, event: dict):
        raise NotImplementedError()


class HttpConnection:

    def __init__(self, event_handler, config):
        assert isinstance(event_handler, HttpConnectionEventHandler)
        self.event_handler: HttpConnectionEventHandler = event_handler

        assert isinstance(config, HABApp.config.Config) or config is None
        self.config: HABApp.config.Config = config

        self.is_online = False
        self.is_read_only = False

        self.__session: aiohttp.ClientSession = None

        self.__host: str = ''
        self.__port: str = ''

        self.__wait = 0

        self.async_try_uuid: asyncio.Future = None

        # automatically update config
        if config is not None:
            self.__update_config_general()
            self.config.openhab.general.subscribe_for_changes(self.__update_config_general)
        else:
            log.error('self.config in http_connection.py is None!')

    def __update_config_general(self):
        self.is_read_only = self.config.openhab.general.listen_only

    def __get_openhab_url(self, url: str, *args, **kwargs) -> str:
        assert not url.startswith('/')
        url = url.format(*args, **kwargs)
        return f'http://{self.__host:s}:{self.__port:d}/{url:s}'

    def __set_offline(self):

        if not self.is_online:
            return None
        self.is_online = False

        self.__wait = 5
        self.event_handler.on_disconnected()

        # Try reconnect
        if not self.async_try_uuid.done():
            self.async_try_uuid.cancel()
        self.async_try_uuid = asyncio.run_coroutine_threadsafe(self._try_uuid(), asyncio.get_event_loop())

    def _is_disconnect_exception(self, e) -> bool:
        if not isinstance(e, (
                # aiohttp Exceptions
                aiohttp.ClientPayloadError, aiohttp.ClientConnectorError,

                # aiohttp_sse_client Exceptions
                ConnectionRefusedError, ConnectionError, ConnectionAbortedError)):
            return False

        self.__set_offline()
        return True

    async def _check_http_response(self, future, additional_info = "") -> typing.Optional[ ClientResponse]:
        try:
            resp = await future
        except Exception as e:
            is_disconnect = self._is_disconnect_exception(e)
            log.log(logging.WARNING if is_disconnect else logging.ERROR, f'{e}')
            if is_disconnect:
                raise OpenhabDisconnectedError()
            else:
                return None

        # Server Errors if openhab is not ready yet
        if resp.status >= 500:
            self.__set_offline()
            raise OpenhabNotReadyYet()

        # Something went wrong - log error message
        if resp.status >= 300:
            # Log Error Message
            additional_info = f' ({additional_info})' if additional_info else ""
            log.warning(f'Status {resp.status} for {resp.request_info.method} {resp.request_info.url}{additional_info}')
            for line in str(resp).splitlines():
                log.debug(line)

        return resp

    def cancel_connect(self):
        if not self.async_try_uuid:
            return None

        if not self.async_try_uuid.done():
            self.async_try_uuid.cancel()

    async def try_connect(self):

        self.cancel_connect()

        # If we are already connected properly disconnect
        if self.__session is not None:
            await self.__session.close()
            self.__session = None

        self.__host: str = self.config.openhab.connection.host
        self.__port: str = self.config.openhab.connection.port

        # do not run without host
        if self.__host == '':
            return None

        auth = None
        if self.config.openhab.connection.user or self.config.openhab.connection.password:
            auth = aiohttp.BasicAuth(
                self.config.openhab.connection.user,
                self.config.openhab.connection.password
            )

        self.__session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=99999999999999999),
            json_serialize=ujson.dumps,
            auth=auth
        )

        self.async_try_uuid = asyncio.ensure_future(self._try_uuid())

    async def _try_uuid(self):

        # sleep before reconnect
        await asyncio.sleep(self.__wait)
        self.__wait *= 2
        self.__wait = min(self.__wait, 180)
        self.__wait = max(5, 0)

        log.debug('Trying to connect to OpenHAB ...')
        try:
            uuid = await self.async_get_uuid()
        except Exception as e:
            if isinstance(e, (OpenhabDisconnectedError, OpenhabNotReadyYet)):
                self.async_try_uuid = asyncio.ensure_future(self._try_uuid())
                log.info(f'... offline!')
            else:
                for l in traceback.format_exc().splitlines():
                    log.error(l)
            return None

        log.info( f'Connected to OpenHAB instance {uuid}')
        self.is_online = True
        self.event_handler.on_connected()
        return None

    async def async_process_sse_events(self):
        try:
            # cache so we don't have to look up every event
            call = self.event_handler.on_sse_event

            async with sse_client.EventSource(
                    self.__get_openhab_url("rest/events?topics=smarthome/items/"),
                    session=self.__session
            ) as event_source:
                async for event in event_source:
                    try:
                        event = ujson.loads(event.data)
                    except ValueError:
                        continue
                    except TypeError:
                        continue

                    # Log sse event
                    if log_events.isEnabledFor(logging.DEBUG):
                        log_events._log(logging.DEBUG, event, [])

                    # process
                    call(event)

        except asyncio.CancelledError:
            pass

        except Exception as e:
            disconnect = self._is_disconnect_exception(e)
            lvl = logging.WARNING if disconnect else logging.ERROR
            log.log(lvl, f'SSE request Error: {e}')
            for l in traceback.format_exc().splitlines():
                log.log(lvl, l)
            if not disconnect:
                raise

    async def async_post_update(self, item, state):

        if self.config.openhab.general.listen_only:
            return False

        fut = self.__session.put(self.__get_openhab_url('rest/items/{item:s}/state', item=item), data=state)
        asyncio.ensure_future(self._check_http_response(fut, additional_info=state))

    async def async_send_command(self, item, state):

        if self.config.openhab.general.listen_only:
            return False

        fut = self.__session.post(self.__get_openhab_url('rest/items/{item:s}', item=item), data=state)
        asyncio.ensure_future(self._check_http_response(fut, additional_info=state))

    async def async_remove_item(self, item_name) -> bool:

        if self.config.openhab.general.listen_only:
            return False

        fut = self.__session.delete(self.__get_openhab_url('rest/items/{:s}', item_name))
        ret = await self._check_http_response(fut)
        return ret.status < 300

    async def async_get_uuid(self) -> str:
        fut = self.__session.get(self.__get_openhab_url('rest/uuid'))
        resp = await self._check_http_response(fut)
        if resp.status >= 300:
            raise OpenhabNotReadyYet()
        return (await resp.text(encoding='utf-8')) if resp else resp

    async def async_get_items(self) -> typing.Optional[list]:
        fut = self.__session.get(
            self.__get_openhab_url('rest/items'),
            json={'recursive': 'false', 'fields': 'state,type,name,editable'}
        )
        try:
            resp = await self._check_http_response(fut)
            return ujson.loads(await resp.text(encoding='utf-8'))
        except Exception as e:
            # sometimes uuid already works but items not - so we ignore these errors here, too
            if not isinstance(e, (OpenhabDisconnectedError, OpenhabNotReadyYet)):
                for l in traceback.format_exc().splitlines():
                    log.error(l)

    async def async_create_item(self, item_type, item_name, label="", category="", tags=[], groups=[]) -> bool:

        if self.config.openhab.general.listen_only:
            return False


        payload = {'type': item_type, 'name': item_name}
        if label:
            payload['label'] = label
        if category:
            payload['category'] = category
        if tags:
            payload['tags'] = tags
        if groups:
            payload['groupnames'] = groups

        fut = self.__session.put(self.__get_openhab_url('rest/items/{:s}', item_name), json=payload)
        ret = await self._check_http_response(fut, payload)
        return ret.status < 300
