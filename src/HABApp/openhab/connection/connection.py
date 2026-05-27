from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import aiohttp

from HABApp.core.connections import (
    AutoReconnectPlugin,
    BaseConnection,
    ConnectionManager,
    ConnectionStateToEventBusPlugin,
)
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from asyncio import Queue
    from collections.abc import AsyncGenerator

    from HABApp.config import ApplicationConfig
    from HABApp.core.internals import EventBus, ItemRegistry
    from HABApp.core.lib import InstantView
    from HABApp.openhab.definitions.websockets.base import BaseOutEvent
    from HABApp.openhab.event_handler import OhEventHandler
    from HABApp.openhab.item_factory import OhItemFactory
    from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
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

    out_queue: Queue[BaseOutEvent]

    @classmethod
    def new_context(cls, *, version: tuple[int, int, int],
                    session: aiohttp.ClientSession, session_options: dict[str, Any],
                    out_queue: Queue[BaseOutEvent]) -> OpenhabContext:
        return cls(
            version=version, is_oh41=version >= (4, 1),
            waited_for_openhab=False,
            created_items={}, created_things={},
            session=session, session_options=session_options,
            out_queue=out_queue
        )


type CONTEXT_TYPE = OpenhabContext | None


@HABAPP_PROVIDER.register
async def setup(
        connection_manager: ConnectionManager, config: ApplicationConfig,
        event_bus: EventBus, item_registry: ItemRegistry,
        item_factory: OhItemFactory, registry_handler: OhItemRegistryHandler, event_handler: OhEventHandler
) -> AsyncGenerator[OpenhabConnection, Any]:

    from HABApp.openhab.connection.handler import HANDLER as CONNECTION_HANDLER
    from HABApp.openhab.connection.plugins import (
        OUTGOING_PLUGIN,
        BrokenLinksPlugin,
        LoadOpenhabItemsPlugin,
        LoadTransformationsPlugin,
        PingPlugin,
        ThingOverviewPlugin,
        WaitForPersistenceRestore,
        WaitForStartlevelPlugin,
        WebsocketPlugin,
    )

    connection = connection_manager.add(OpenhabConnection())
    connection.register_plugin(CONNECTION_HANDLER)

    connection.register_plugin(WaitForStartlevelPlugin(), 0)
    connection.register_plugin(OUTGOING_PLUGIN, 10)
    connection.register_plugin(
        LoadOpenhabItemsPlugin(
            'LoadItemsAndThings',
            item_factory=item_factory, registry_handler=registry_handler, item_registry=item_registry
        ),
        20
    )
    connection.register_plugin(WebsocketPlugin(event_handler=event_handler), 30)
    connection.register_plugin(
        LoadOpenhabItemsPlugin(
            'SyncItemsAndThings',
            item_factory=item_factory, registry_handler=registry_handler, item_registry=item_registry
        ),
        40
    )
    connection.register_plugin(LoadTransformationsPlugin(), 50)
    connection.register_plugin(PingPlugin(item_registry=item_registry, event_bus=event_bus), 100)
    connection.register_plugin(WaitForPersistenceRestore(item_registry=item_registry), 110)
    connection.register_plugin(ThingOverviewPlugin(), 500_000)
    connection.register_plugin(BrokenLinksPlugin(item_registry=item_registry), 500_001)

    connection.register_plugin(ConnectionStateToEventBusPlugin(event_bus=event_bus))
    connection.register_plugin(AutoReconnectPlugin())

    # config changes
    config.openhab.general.subscribe_for_changes(CONNECTION_HANDLER.update_cfg_general)

    yield connection

    connection.on_application_shutdown()


class OpenhabConnection(BaseConnection):
    def __init__(self) -> None:
        super().__init__('openhab')
        self.context: CONTEXT_TYPE = None

    def is_silent_exception(self, e: Exception) -> bool:
        from HABApp.openhab.connection.plugins.websockets import WebSocketClosedError

        return isinstance(e, (
            # https://docs.aiohttp.org/en/stable/client_reference.html#client-exceptions
            aiohttp.ClientError,

            # Websocket exceptions
            WebSocketClosedError,

            # aiohttp_sse_client Exceptions
            ConnectionRefusedError, ConnectionError, ConnectionAbortedError)
        )
