from __future__ import annotations

from typing import Any, Final

from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.connections._definitions import CONNECTION_HANDLER_NAME
from HABApp.core.connections.base_connection import AlreadyHandledException
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler import OhClientSession, OpenHabAsyncInterface
from HABApp.openhab.errors import OpenhabCredentialsInvalidError, OpenhabDisconnectedError


# noinspection PyProtectedMember
class ConnectionHandler(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, *, interface: OpenHabAsyncInterface, session: OhClientSession) -> None:
        super().__init__(name=CONNECTION_HANDLER_NAME)
        self._interface: Final = interface
        self.options: dict[str, Any] = {}
        self.read_only: bool = False
        self.online = False
        self.session: Final = session

    def update_cfg_general(self) -> None:
        cfg: Final = CONFIG.openhab.general
        self.session.update_cfg(cfg)

    async def on_connected(self) -> None:
        self.online = True

    async def on_connecting(self, connection: OpenhabConnection) -> None:
        log = self.plugin_connection.log
        log.debug('Trying to connect to OpenHAB ...')

        try:
            if (root := await self._interface.get_root_or_none()) is None:
                connection.set_error()
                log.info('... offline!')
                return None

            info = root.runtime_info
            log.info(f'Connected {"read only " if self.read_only else ""}to OpenHAB '
                     f'version {info.version:s} ({info.build_string:s})')

            vers = tuple(int(_v) for _v in info.version.split('.')[:3])
            if vers < (4, 0):
                log.error('HABApp requires at least openHAB version 4.0!')

            connection.context = OpenhabContext.new_context(version=vers)

        # during startup we get OpenhabCredentialsInvalidError even though credentials are correct
        except (OpenhabDisconnectedError, OpenhabCredentialsInvalidError):
            connection.set_error()
            raise AlreadyHandledException() from None

    async def on_disconnected(self, connection: OpenhabConnection) -> None:
        self.online = False
        connection.context = None
