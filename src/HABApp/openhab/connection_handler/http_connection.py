import asyncio
import logging
import traceback
import typing
from asyncio import Queue, sleep, QueueEmpty
from typing import Any, Optional, Final

import aiohttp
from aiohttp.client import ClientResponse, _RequestContextManager
from aiohttp.hdrs import METH_GET, METH_POST, METH_PUT, METH_DELETE
from aiohttp_sse_client import client as sse_client

import HABApp
import HABApp.core
import HABApp.openhab.events
from HABApp.core.asyncio import async_context
from HABApp.core.const.json import dump_json, load_json
from HABApp.core.logger import log_info, log_warning
from HABApp.core.wrapper import process_exception, ignore_exception
from HABApp.openhab.errors import OpenhabDisconnectedError, ExpectedSuccessFromOpenhab
from .http_connection_waiter import WaitBetweenConnects
from ...core.const.topics import TOPIC_EVENTS
from ...core.lib import SingleTask

log = logging.getLogger('HABApp.openhab.connection')
log_events = logging.getLogger(f'{TOPIC_EVENTS}.openhab')


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

    TASK_QUEUE_WORKER.cancel()
    TASK_QUEUE_WATCHER.cancel()

    await asyncio.sleep(0)

    # If we are already connected properly disconnect
    if HTTP_SESSION is not None:
        await HTTP_SESSION.close()
        HTTP_SESSION = None


async def setup_connection():
    global HTTP_SESSION, HTTP_VERIFY_SSL

    await shutdown_connection()

    config = HABApp.CONFIG.openhab
    url: str = config.connection.url
    user: str = config.connection.user
    password: str = config.connection.password

    # do not run without an url
    if not url:
        log_info(log, 'openHAB connection disabled (url missing)!')
        return None

    # do not run without user/pw - since OH3 mandatory
    if not user or not password:
        log_info(log, 'openHAB connection disabled (user/password missing)!')
        return None

    if not config.connection.verify_ssl:
        HTTP_VERIFY_SSL = False
        log.info('Verify ssl set to False!')
    else:
        HTTP_VERIFY_SSL = None

    HTTP_SESSION = aiohttp.ClientSession(
        base_url=url,
        timeout=aiohttp.ClientTimeout(total=None),
        json_serialize=dump_json,
        auth=aiohttp.BasicAuth(user, password),
        read_bufsize=int(config.connection.buffer),
    )

    TASK_TRY_CONNECT.start()


async def start_sse_event_listener():

    async_context.set('SSE')

    try:
        # cache so we don't have to look up every event
        _load_json = load_json
        _see_handler = on_sse_event

        async with sse_client.EventSource(url=f'/rest/events?topics={HABApp.CONFIG.openhab.connection.topic_filter}',
                                          session=HTTP_SESSION, ssl=HTTP_VERIFY_SSL) as event_source:
            async for event in event_source:

                e_str = event.data

                try:
                    e_json = _load_json(e_str)
                except (ValueError, TypeError):
                    log_events.warning(f'Invalid json: {e_str}')
                    continue

                # Alive event from openhab to detect dropped connections
                # -> Can be ignored on the HABApp side
                if e_json.get('type') == 'ALIVE':
                    continue

                # Log raw sse event
                if log_events.isEnabledFor(logging.DEBUG):
                    log_events._log(logging.DEBUG, e_str, [])

                # process
                _see_handler(e_json)
    except Exception as e:
        disconnect = is_disconnect_exception(e)
        lvl = logging.WARNING if disconnect else logging.ERROR
        log.log(lvl, f'SSE request Error: {e}')
        for line in traceback.format_exc().splitlines():
            log.log(lvl, line)

        # reconnect even if we have an unexpected error
        if not disconnect:
            set_offline(f'Uncaught error in process_sse_events: {e}')


QUEUE = Queue()


async def output_queue_listener():
    # clear Queue
    try:
        while True:
            await QUEUE.get_nowait()
    except QueueEmpty:
        pass

    while True:
        try:
            while True:
                item, state, is_cmd = await QUEUE.get()

                if not isinstance(state, str):
                    state = convert_to_oh_type(state)

                if is_cmd:
                    await post(f'/rest/items/{item:s}', data=state)
                else:
                    await put(f'/rest/items/{item:s}/state', data=state)
        except Exception as e:
            process_exception(output_queue_listener, e, logger=log)


@ignore_exception
async def output_queue_check_size():

    first_msg_at = 150

    upper = first_msg_at
    lower = -1
    last_info_at = first_msg_at // 2

    while True:
        await sleep(5)
        size = QUEUE.qsize()

        # small log msg
        if size > upper:
            upper = size * 2
            lower = size // 2
            log_warning(log, f'{size} messages in queue')
        elif size < lower:
            upper = max(size / 2, first_msg_at)
            lower = size // 2
            if lower <= last_info_at:
                lower = -1
                log_info(log, 'queue OK')
            else:
                log_info(log, f'{size} messages in queue')


async def async_post_update(item, state: Any):
    QUEUE.put_nowait((item, state, False))


async def async_send_command(item, state: Any):
    QUEUE.put_nowait((item, state, True))


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


async def async_get_start_level(default_level: int = -10) -> int:
    system_info = await async_get_system_info()
    return system_info.get('systemInfo', {}).get('startLevel', default_level)


async def wait_for_min_start_level():

    waited_for_oh = False
    last_level = -100

    while True:
        start_level_is = await async_get_start_level()
        start_level_min = HABApp.CONFIG.openhab.general.min_start_level
        if start_level_is >= start_level_min:
            break

        # show msg only once
        if not waited_for_oh:
            log.info('Waiting for openHAB startup to be complete')

        # show start level change
        if last_level != start_level_is:
            log.debug(f'Startlevel: {start_level_is}')
        last_level = start_level_is

        # wait for openhab
        waited_for_oh = True
        await asyncio.sleep(1)

    # Startup complete
    if waited_for_oh:
        log.info('openHAB startup complete')


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
            if not runtime_info:
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
            await wait_for_min_start_level()
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

    # output messages
    TASK_QUEUE_WORKER.start()
    TASK_QUEUE_WATCHER.start()

    ON_CONNECTED()
    return None


TASK_SSE_LISTENER: Final = SingleTask(start_sse_event_listener, 'SSE event listener')
TASK_TRY_CONNECT: Final = SingleTask(try_connect, 'Try OH connect')

TASK_QUEUE_WORKER: Final = SingleTask(output_queue_listener, 'OhQueue')
TASK_QUEUE_WATCHER: Final = SingleTask(output_queue_check_size, 'OhQueueSize')


def __load_cfg():
    global IS_READ_ONLY
    IS_READ_ONLY = HABApp.config.CONFIG.openhab.general.listen_only


# setup config
__load_cfg()
HABApp.config.CONFIG.subscribe_for_changes(__load_cfg)


# import it here otherwise we get cyclic imports
from HABApp.openhab.connection_handler.sse_handler import on_sse_event  # noqa: E402
from HABApp.openhab.connection_handler.func_async import convert_to_oh_type  # noqa: E402
