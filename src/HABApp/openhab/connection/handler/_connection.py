from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from aiohttp.client import ClientResponse, _RequestContextManager
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST, METH_PUT
from aiohttp.typedefs import Query as _Query

from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.core.shutdown import ShutdownInfo
from HABApp.openhab.errors import OpenhabCredentialsInvalidError, OpenhabDisconnectedError


if TYPE_CHECKING:

    from aiohttp import ClientSession

    from HABApp.config.models.openhab import General as OhGeneralConfig
    from HABApp.openhab.connection.connection import OpenhabConnection


# noinspection PyProtectedMember
class OhClientSession:
    # no slots because otherwise we can't monkeypatch the session for testing
    # __slots__ = ('_connection', '_request', '_session', 'options', 'read_only')  # noqa: ERA001

    def __init__(self, session: ClientSession, connection: OpenhabConnection, *,
                 ssl: bool) -> None:

        self._ssl: Final = ssl
        self._session: Final = session
        self._connection: Final = connection
        self._request = self._session.request
        self.read_only: bool = False

    @property
    def aiohttp_session(self) -> ClientSession:
        return self._session

    def update_cfg(self, cfg: OhGeneralConfig) -> None:
        self.read_only = cfg.listen_only

    async def get(self, url: str, *, log_404: bool = True,
                  params: _Query | None = None, **kwargs: Any) -> ClientResponse:

        mgr = _RequestContextManager(self._request(METH_GET, url, params=params, ssl=self._ssl, **kwargs))
        return await self.check_response(mgr, log_404=log_404)

    async def post(self, url: str, *, log_404: bool = True, json: dict[str, Any] | None = None,
                   data: str | None = None, params: _Query | None = None, **kwargs: Any) -> ClientResponse | None:

        if self.read_only:
            return None

        mgr = _RequestContextManager(
            self._request(METH_POST, url, data=data, json=json, params=params, ssl=self._ssl, **kwargs)
        )
        if data is None:
            data = json
        return await self.check_response(mgr, log_404=log_404, sent_data=data)

    async def put(self, url: str, *, log_404: bool = True, json: dict[str, Any] | None = None,
                  data: str | None = None, params: _Query | None = None, **kwargs: Any) -> ClientResponse | None:

        if self.read_only:
            return None

        mgr = _RequestContextManager(
            self._request(METH_PUT, url, data=data, json=json, params=params, ssl=self._ssl, **kwargs)
        )
        if data is None:
            data = json
        return await self.check_response(mgr, log_404=log_404, sent_data=data)

    async def delete(self, url: str, *, log_404: bool = True, json: dict[str, Any] | None = None,
                     data: str | None = None, params: _Query | None = None, **kwargs: Any) -> ClientResponse | None:

        if self.read_only:
            return None

        mgr = _RequestContextManager(
            self._request(METH_DELETE, url, data=data, json=json, params=params, ssl=self._ssl, **kwargs)
        )
        if data is None:
            data = json
        return await self.check_response(mgr, log_404=log_404, sent_data=data)

    async def check_response(self, future: _RequestContextManager, *,
                             sent_data: str | dict | None = None, log_404: bool = True) -> ClientResponse:
        try:
            resp = await future
        except Exception as e:
            self._connection.process_exception(e, None)
            if self._session.closed:
                # We can not recover from a closed session so we shut down
                self._connection.log.error('Session closed!')
                HABAPP_PROVIDER.get_existing(ShutdownInfo).request_shutdown()
            raise OpenhabDisconnectedError() from None

        if (status := resp.status) < 300:  # noqa: PLR2004
            return resp

        if status == 404 and not log_404:  # noqa: PLR2004
            return resp

        # Log Error Message
        sent = '' if sent_data is None else f' {sent_data}'
        self._connection.log.warning(f'Status {status} for {resp.request_info.method} {resp.request_info.url}{sent}')
        for line in str(resp).splitlines():
            self._connection.log.debug(line)

        if resp.status == 401:  # noqa: PLR2004
            raise OpenhabCredentialsInvalidError()

        return resp
