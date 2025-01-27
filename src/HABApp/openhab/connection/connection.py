from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias

import aiohttp

import HABApp
from HABApp.core.connections import AutoReconnectPlugin, BaseConnection, Connections, ConnectionStateToEventBusPlugin


if TYPE_CHECKING:
    from asyncio import Queue

    from HABApp.core.lib import InstantView
    from HABApp.openhab.items import OpenhabItem, Thing


@dataclass
class OpenhabContext:
    version: tuple[int, int, int]
    is_oh41: bool

    # true when we waited during connect
    waited_for_openhab: bool

    created_items: dict[str, tuple[OpenhabItem, InstantView]]
    created_things: dict[str, tuple[Thing, InstantView]]

    session: aiohttp.ClientSession
    session_options: dict[str, Any]

    out_queue: Queue[tuple[str, str, bool]]

    @classmethod
    def new_context(cls, *, version: tuple[int, int, int],
                    session: aiohttp.ClientSession, session_options: dict[str, Any],
                    out_queue: Queue[tuple[str, str, bool]]) -> OpenhabContext:
        return cls(
            version=version, is_oh41=version >= (4, 1),
            waited_for_openhab=False,
            created_items={}, created_things={},
            session=session, session_options=session_options,
            out_queue=out_queue
        )


CONTEXT_TYPE: TypeAlias = OpenhabContext | None


def setup() -> None:
    config = HABApp.config.CONFIG.openhab

    from HABApp.openhab.connection.handler import HANDLER as CONNECTION_HANDLER
    from HABApp.openhab.connection.plugins import (
        OUTGOING_PLUGIN,
        BrokenLinksPlugin,
        LoadOpenhabItemsPlugin,
        LoadTransformationsPlugin,
        PingPlugin,
        TextualThingConfigPlugin,
        ThingOverviewPlugin,
        WaitForPersistenceRestore,
        WaitForStartlevelPlugin,
        WebsocketPlugin,
    )

    connection = Connections.add(OpenhabConnection())
    connection.register_plugin(CONNECTION_HANDLER)

    connection.register_plugin(WaitForStartlevelPlugin(), 0)
    connection.register_plugin(OUTGOING_PLUGIN, 10)
    connection.register_plugin(LoadOpenhabItemsPlugin('LoadItemsAndThings'), 20)
    connection.register_plugin(WebsocketPlugin(), 30)
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
    def __init__(self) -> None:
        super().__init__('openhab')
        self.context: CONTEXT_TYPE = None

    def is_silent_exception(self, e: Exception) -> bool:
        return isinstance(e, (
            # https://docs.aiohttp.org/en/stable/client_reference.html#client-exceptions
            aiohttp.ClientError,

            # aiohttp_sse_client Exceptions
            ConnectionRefusedError, ConnectionError, ConnectionAbortedError)
        )
