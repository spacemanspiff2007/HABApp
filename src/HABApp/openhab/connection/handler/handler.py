from __future__ import annotations

from asyncio import Queue
from typing import Any, Final

import aiohttp
from aiohttp.client import ClientResponse, _RequestContextManager
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST, METH_PUT

from HABApp.config import CONFIG
from HABApp.core import shutdown
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.connections._definitions import CONNECTION_HANDLER_NAME
from HABApp.core.connections.base_connection import AlreadyHandledException
from HABApp.core.const.json import dump_json
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.errors import OpenhabCredentialsInvalidError, OpenhabDisconnectedError


# noinspection PyProtectedMember
class ConnectionHandler(BaseConnectionPlugin[OpenhabConnection]):
    request: aiohttp.ClientSession._request

    def __init__(self) -> None:
        super().__init__(name=CONNECTION_HANDLER_NAME)
        self.options: dict[str, Any] = {}
        self.read_only: bool = False
        self.online = False
        self.session: aiohttp.ClientSession | None = None

    def update_cfg_general(self) -> None:
        self.read_only = CONFIG.openhab.general.listen_only

    async def on_setup(self, connection: OpenhabConnection) -> None:
        log = self.plugin_connection.log
        config = CONFIG.openhab.connection
        url: str = config.url
        user: str = config.user
        password: str = config.password

        # do not run without an url
        if not url:
            log.info('Connection disabled (url missing)!')
            connection.status_from_setup_to_disabled()
            return None

        # do not run without user/pw - since OH3 mandatory
        is_token = user.startswith('oh.') or password.startswith('oh.')
        if not is_token and (not user or not password):
            log.info('Connection disabled (user/password missing)!')
            connection.status_from_setup_to_disabled()
            return None

        if not config.verify_ssl:
            self.options['ssl'] = False
            log.info('Verify ssl set to False!')
        else:
            self.options.pop('ssl', None)

        self.update_cfg_general()

        # remove existing session
        if (s := self.session) is not None:
            self.session = None
            await s.close()

        self.session = aiohttp.ClientSession(
            base_url=url,
            timeout=aiohttp.ClientTimeout(total=None),
            json_serialize=dump_json,
            auth=aiohttp.BasicAuth(user, password),
        )
        self.request = self.session._request

    async def on_connected(self) -> None:
        self.online = True

    async def on_shutdown(self) -> None:
        if self.session is None:
            return None

        await self.session.close()
        self.session = None

    async def get(self, url: str, log_404=True, **kwargs: Any) -> ClientResponse:
        mgr = _RequestContextManager(self.request(METH_GET, url, **self.options, **kwargs))
        return await self.check_response(mgr, log_404=log_404)

    async def post(self, url: str, log_404=True, json=None, data=None, **kwargs: Any) -> ClientResponse | None:
        if self.read_only or not self.online:
            return None

        mgr = _RequestContextManager(
            self.request(METH_POST, url, data=data, json=json, **self.options, **kwargs)
        )
        if data is None:
            data = json
        return await self.check_response(mgr, log_404=log_404, sent_data=data)

    async def put(self, url: str, log_404=True, json=None, data=None, **kwargs: Any) -> ClientResponse | None:
        if self.read_only or not self.online:
            return None

        mgr = _RequestContextManager(
            self.request(METH_PUT, url, data=data, json=json, **self.options, **kwargs)
        )
        if data is None:
            data = json
        return await self.check_response(mgr, log_404=log_404, sent_data=data)

    async def delete(self, url: str, log_404=True, json=None, data=None, **kwargs: Any) -> ClientResponse | None:
        if self.read_only or not self.online:
            return None

        mgr = _RequestContextManager(
            self.request(METH_DELETE, url, data=data, json=json, **self.options, **kwargs)
        )
        if data is None:
            data = json
        return await self.check_response(mgr, log_404=log_404, sent_data=data)

    async def check_response(self, future: aiohttp.client._RequestContextManager, sent_data=None,
                             log_404=True) -> ClientResponse:
        try:
            resp = await future
        except Exception as e:
            self.plugin_connection.process_exception(e, None)
            if self.session.closed:
                # We can not recover from a closed session so we shutdown
                self.plugin_connection.log.error('Session closed!')
                shutdown.request()
            raise OpenhabDisconnectedError() from None

        if (status := resp.status) < 300:
            return resp

        if status == 404 and not log_404:
            return resp

        # Log Error Message
        log = self.plugin_connection.log
        sent = '' if sent_data is None else f' {sent_data}'
        log.warning(f'Status {status} for {resp.request_info.method} {resp.request_info.url}{sent}')
        for line in str(resp).splitlines():
            log.debug(line)

        if resp.status == 401:
            raise OpenhabCredentialsInvalidError()

        return resp

    async def on_connecting(self, connection: OpenhabConnection) -> None:
        from HABApp.openhab.connection.handler.func_async import async_get_root

        log = self.plugin_connection.log
        log.debug('Trying to connect to OpenHAB ...')

        try:
            if (root := await async_get_root()) is None:
                connection.set_error()
                log.info('... offline!')
                return None

            info = root.runtime_info
            log.info(f'Connected {"read only " if self.read_only else ""}to OpenHAB '
                     f'version {info.version:s} ({info.build_string:s})')

            vers = tuple(int(_v) for _v in info.version.split('.')[:3])
            if vers < (4, 0):
                log.error('HABApp requires at least openHAB version 4.0!')

            connection.context = OpenhabContext.new_context(
                version=vers, session=self.session, session_options=self.options,
                out_queue=Queue()
            )

        # during startup we get OpenhabCredentialsInvalidError even though credentials are correct
        except (OpenhabDisconnectedError, OpenhabCredentialsInvalidError):
            connection.set_error()
            raise AlreadyHandledException() from None

    async def on_disconnected(self, connection: OpenhabConnection) -> None:
        self.online = False
        connection.context = None


HANDLER: Final = ConnectionHandler()
get: Final = HANDLER.get
post: Final = HANDLER.post
put: Final = HANDLER.put
delete: Final = HANDLER.delete
