from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

import aiohttp

import HABApp
from HABApp.core.connections import AutoReconnectPlugin, BaseConnection, Connections, ConnectionStateToEventBusPlugin
from HABApp.core.const.const import PYTHON_310
from HABApp.core.items.base_valueitem import datetime

if PYTHON_310:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from HABApp.openhab.items import OpenhabItem, Thing


@dataclass
class OpenhabContext:
    version: tuple[int, int, int]
    is_oh3: bool

    # true when we waited during connect
    waited_for_openhab: bool

    created_items: dict[str, tuple[OpenhabItem, datetime]]
    created_things: dict[str, tuple[Thing, datetime]]

    session: aiohttp.ClientSession
    session_options: dict[str, Any]


CONTEXT_TYPE: TypeAlias = Optional[OpenhabContext]


def setup():
    config = HABApp.config.CONFIG.openhab

    from HABApp.openhab.connection.handler import HANDLER as CONNECTION_HANDLER
    from HABApp.openhab.connection.plugins import (WaitForStartlevelPlugin, LoadOpenhabItemsPlugin,
                                                   SseEventListenerPlugin, OUTGOING_PLUGIN, LoadTransformationsPlugin,
                                                   WaitForPersistenceRestore, PingPlugin, ThingOverviewPlugin,
                                                   TextualThingConfigPlugin, BrokenLinksPlugin)

    connection = Connections.add(OpenhabConnection())
    connection.register_plugin(CONNECTION_HANDLER)

    connection.register_plugin(WaitForStartlevelPlugin(), 0)
    connection.register_plugin(OUTGOING_PLUGIN, 10)
    connection.register_plugin(LoadOpenhabItemsPlugin('LoadItemsAndThings'), 20)
    connection.register_plugin(SseEventListenerPlugin(), 30)
    connection.register_plugin(LoadOpenhabItemsPlugin('SyncItemsAndThings'), 40)
    connection.register_plugin(LoadTransformationsPlugin(), 50)
    connection.register_plugin(PingPlugin(), 100)
    connection.register_plugin(WaitForPersistenceRestore(), 110)
    connection.register_plugin(TextualThingConfigPlugin(), 120)
    connection.register_plugin(ThingOverviewPlugin(), 500_000)
    connection.register_plugin(BrokenLinksPlugin(), 500_001)

    connection.register_plugin(ConnectionStateToEventBusPlugin())
    connection.register_plugin(AutoReconnectPlugin())

    # config changes
    config.general.subscribe_for_changes(CONNECTION_HANDLER.update_cfg_general)


class OpenhabConnection(BaseConnection):
    def __init__(self):
        super().__init__('openhab')
        self.context: CONTEXT_TYPE = None

    def is_silent_exception(self, e: Exception):
        return isinstance(e, (
            # aiohttp Exceptions
            aiohttp.ClientPayloadError, aiohttp.ClientConnectorError, aiohttp.ClientOSError,

            # aiohttp_sse_client Exceptions
            ConnectionRefusedError, ConnectionError, ConnectionAbortedError)
        )
