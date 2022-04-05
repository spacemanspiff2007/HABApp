import asyncio
import logging
import traceback
import typing
from typing import Any, Optional, Final

import aiohttp
from aiohttp.client import ClientResponse, _RequestContextManager
from aiohttp.hdrs import METH_GET, METH_POST, METH_PUT, METH_DELETE
from aiohttp_sse_client import client as sse_client

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.const.json import dump_json, load_json
from HABApp.core.logger import log_error
from HABApp.openhab.errors import OpenhabDisconnectedError, ExpectedSuccessFromOpenhab
from .http_connection_waiter import WaitBetweenConnects
from ...core.lib import SingleTask

log = logging.getLogger('HABApp.openhab.connection')
log_events = logging.getLogger('HABApp.EventBus.openhab')


IS_ONLINE: bool = False
IS_READ_ONLY: bool = False


# HTTP options
HTTP_ALLOW_REDIRECTS: bool = True
HTTP_VERIFY_SSL: Optional[bool] = None
HTTP_SESSION: aiohttp.ClientSession = None

CONNECT_WAIT: WaitBetweenConnects = WaitBetweenConnects()

ON_CONNECTED: typing.Callable = None
ON_DISCONNECTED: typing.Callable = None


async def get(url: str, log_404=True, **kwargs: Any) -> ClientResponse:

    mgr = _RequestContextManager(
        HTTP_SESSION._request(METH_GET, url, allow_redirects=HTTP_ALLOW_REDIRECTS, ssl=HTTP_VERIFY_SSL, **kwargs)
    )
    return await check_response(mgr, log_404=log_404)


async def post(url: str, log_404=True, json=None, data=None, **kwargs: Any) -> Optional[ClientResponse]:

    if IS_READ_ONLY or not IS_ONLINE:
        return None

    mgr = _RequestContextManager(
        HTTP_SESSION._request(
            METH_POST, url, allow_redirects=HTTP_ALLOW_REDIRECTS, ssl=HTTP_VERIFY_SSL,
            data=data, json=json, **kwargs
        )
    )

    if data is None:
        data = json
    return await check_response(mgr, log_404=log_404, sent_data=data)


async def put(url: str, log_404=True, json=None, data=None, **kwargs: Any) -> Optional[ClientResponse]:

    if IS_READ_ONLY or not IS_ONLINE:
        return None

    mgr = _RequestContextManager(
        HTTP_SESSION._request(
            METH_PUT, url, allow_redirects=HTTP_ALLOW_REDIRECTS, ssl=HTTP_VERIFY_SSL,
            data=data, json=json, **kwargs
        )
    )

    if data is None:
        data = json
    return await check_response(mgr, log_404=log_404, sent_data=data)


async def delete(url: str, log_404=True, json=None, data=None, **kwargs: Any) -> Optional[ClientResponse]:

    if IS_READ_ONLY or not IS_ONLINE:
        return None

    mgr = _RequestContextManager(
        HTTP_SESSION._request(METH_DELETE, url, allow_redirects=HTTP_ALLOW_REDIRECTS, ssl=HTTP_VERIFY_SSL,
                              data=data, json=json, **kwargs)
    )

    if data is None:
        data = json
    return await check_response(mgr, log_404=log_404, sent_data=data)


def set_offline(log_msg=''):
    global IS_ONLINE

    if not IS_ONLINE:
        return None
    IS_ONLINE = False

    log.warning(f'Disconnected! {log_msg}')

    # cancel SSE listener
    TASK_SSE_LISTENER.cancel()
    TASK_TRY_CONNECT.cancel()

    ON_DISCONNECTED()

    TASK_TRY_CONNECT.start()


def is_disconnect_exception(e) -> bool:
    if not isinstance(e, (
            # aiohttp Exceptions
            aiohttp.ClientPayloadError, aiohttp.ClientConnectorError, aiohttp.ClientOSError,

            # aiohttp_sse_client Exceptions
            ConnectionRefusedError, ConnectionError, ConnectionAbortedError)):
        return False

    set_offline(str(e))
    return True


async def check_response(future: aiohttp.client._RequestContextManager, sent_data=None,
                         log_404=True, disconnect_on_error=False) -> ClientResponse:
    try:
        resp = await future
    except Exception as e:
        is_disconnect = is_disconnect_exception(e)
        log.log(logging.WARNING if is_disconnect else logging.ERROR, f'"{e}" ({type(e)})')
        if is_disconnect:
            raise OpenhabDisconnectedError()
        raise

    status = resp.status

    # Sometimes openHAB issues 404 instead of 500 during startup
    if disconnect_on_error and status >= 400:
        set_offline(f'Expected success but got status {status} for '
                    f'{str(resp.request_info.url).replace(HABApp.CONFIG.openhab.connection.url, "")}')
        raise ExpectedSuccessFromOpenhab()

    # Something went wrong - log error message
    log_msg = False
    if status >= 300:
        log_msg = True

        # possibility skip logging of 404
        if status == 404 and not log_404:
            log_msg = False

    if log_msg:
        # Log Error Message
        sent = '' if sent_data is None else f' {sent_data}'
        log.warning(f'Status {status} for {resp.request_info.method} {resp.request_info.url}{sent}')
        for line in str(resp).splitlines():
            log.debug(line)

    return resp


async def shutdown_connection():
    global HTTP_SESSION

    TASK_TRY_CONNECT.cancel()
    TASK_SSE_LISTENER.cancel()

    await asyncio.sleep(0)

    # If we are already connected properly disconnect
    if HTTP_SESSION is not None:
        await HTTP_SESSION.close()
        HTTP_SESSION = None


async def setup_connection():
    global HTTP_SESSION, FUT_UUID, HTTP_VERIFY_SSL

    await shutdown_connection()

    url: str = HABApp.CONFIG.openhab.connection.url

    # do not run without an url
    if url == '':
        log_error(log, 'No URL configured for openHAB!')
        return None

    if not HABApp.CONFIG.openhab.connection.verify_ssl:
        HTTP_VERIFY_SSL = False
        log.info('Verify ssl set to False!')
    else:
        HTTP_VERIFY_SSL = None

    # todo: add possibility to configure line size with read_bufsize
    HTTP_SESSION = aiohttp.ClientSession(
        base_url=url,
        timeout=aiohttp.ClientTimeout(total=None),
        json_serialize=dump_json,
        auth=aiohttp.BasicAuth(HABApp.CONFIG.openhab.connection.user, HABApp.CONFIG.openhab.connection.password),
        read_bufsize=2**19  # 512k buffer,
    )

    TASK_TRY_CONNECT.start()


async def start_sse_event_listener():
    try:
        # cache so we don't have to look up every event
        _load_json = load_json
        _see_handler = on_sse_event

        async with sse_client.EventSource(
                url='/rest/events?topics='
                    'openhab/items/,'       # Item updates
                    'openhab/channels/,'    # Channel update
                    'openhab/things/',      # Thing updates
                session=HTTP_SESSION,
                ssl=None if HABApp.CONFIG.openhab.connection.verify_ssl else False
        ) as event_source:
            async for event in event_source:

                e_str = event.data

                try:
                    e_json = _load_json(e_str)
                except ValueError:
                    log_events.warning(f'Invalid json: {e_str}')
                    continue
                except TypeError:
                    log_events.warning(f'Invalid json: {e_str}')
                    continue

                # Log sse event
                if log_events.isEnabledFor(logging.DEBUG):
                    log_events._log(logging.DEBUG, e_str, [])

                # process
                _see_handler(e_json)

    except asyncio.CancelledError:
        # This exception gets raised if we cancel the coroutine
        # since this is normal behaviour we ignore this exception
        pass
    except Exception as e:
        disconnect = is_disconnect_exception(e)
        lvl = logging.WARNING if disconnect else logging.ERROR
        log.log(lvl, f'SSE request Error: {e}')
        for line in traceback.format_exc().splitlines():
            log.log(lvl, line)

        # reconnect even if we have an unexpected error
        if not disconnect:
            set_offline(f'Uncaught error in process_sse_events: {e}')


async def async_get_uuid() -> str:
    resp = await get('/rest/uuid', log_404=False)
    return await resp.text(encoding='utf-8')


async def async_get_root() -> dict:
    resp = await get('/rest/', log_404=False)
    if resp.status == 404:
        return {}
    return await resp.json(loads=load_json, encoding='utf-8')


async def async_get_system_info() -> dict:
    resp = await get('/rest/systeminfo', log_404=False)
    if resp.status == 404:
        return {}
    return await resp.json(loads=load_json, encoding='utf-8')


async def try_connect():
    global IS_ONLINE

    while True:
        try:
            # sleep before reconnect
            await CONNECT_WAIT.wait()

            log.debug('Trying to connect to OpenHAB ...')
            root = await async_get_root()

            # It's possible that we get status 4XX during startup and then the response is empty
            runtime_info = root.get('runtimeInfo')
            if runtime_info is None:
                log.info('... offline!')
                continue

            log.info(f'Connected {"read only " if IS_READ_ONLY else ""}to OpenHAB '
                     f'version {runtime_info["version"]} ({runtime_info["buildString"]})')

            # todo: remove this 2023
            # Show warning (convenience)
            vers = tuple(map(int, runtime_info["version"].split('.')[:2]))
            if vers < (3, 3):
                log.warning('HABApp requires at least openHAB version 3.3!')

            # wait for openhab startup to be complete
            last_level = -100
            while True:
                system_info = await async_get_system_info()
                start_lvl = system_info.get('systemInfo', {}).get('startLevel', -1)
                if start_lvl >= 100:
                    break

                # initial msg
                if last_level == -100:
                    log.info('Waiting for openHAB startup to be complete')

                # show current status
                if last_level != start_lvl:
                    log.debug(f'Startlevel: {start_lvl}')
                last_level = start_lvl

                await asyncio.sleep(1)

            # Startup complete
            if last_level != -100:
                log.info('openHAB startup complete')
            break
        except Exception as e:
            if isinstance(e, (OpenhabDisconnectedError, ExpectedSuccessFromOpenhab)):
                log.info('... offline!')
            else:
                for line in traceback.format_exc().splitlines():
                    log.error(line)

    IS_ONLINE = True

    # start sse processing
    TASK_SSE_LISTENER.start()

    ON_CONNECTED()
    return None


TASK_SSE_LISTENER: Final = SingleTask(start_sse_event_listener, 'SSE event listener')
TASK_TRY_CONNECT: Final = SingleTask(try_connect, 'Try OH connect')


def __load_cfg():
    global IS_READ_ONLY
    IS_READ_ONLY = HABApp.config.CONFIG.openhab.general.listen_only


# setup config
__load_cfg()
HABApp.config.CONFIG.subscribe_for_changes(__load_cfg)


# import it here otherwise we get cyclic imports
from HABApp.openhab.connection_handler.sse_handler import on_sse_event  # noqa: E402
