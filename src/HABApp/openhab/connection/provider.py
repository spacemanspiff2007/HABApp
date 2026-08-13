from __future__ import annotations

import contextlib
import logging
from asyncio import CancelledError
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, Final
from unittest.mock import Mock

import aiohttp

from HABApp.core.connections import (
    AutoReconnectPlugin,
    ConnectionManager,
    ConnectionStateToEventBusPlugin,
)
from HABApp.core.const.json import dump_json
from HABApp.core.lib import WatchedSingleConsumerQueue
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.openhab.connection.connection import OhHttpQueue, OhWebsocketQueue, OpenhabConnection
from HABApp.openhab.connection.handler import OhClientSession, OpenHabAsyncInterface
from HABApp.openhab.connection.handler.handler import ConnectionHandler
from HABApp.openhab.connection.plugins import (
    BrokenLinksPlugin,
    LoadOpenhabItemsPlugin,
    LoadTransformationsPlugin,
    OutgoingCommandsPlugin,
    PingPlugin,
    ThingOverviewPlugin,
    WaitForPersistenceRestore,
    WaitForStartlevelPlugin,
    WebsocketPlugin,
)


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from HABApp.config import ApplicationConfig
    from HABApp.core.internals import EventBus, ItemRegistry
    from HABApp.core.lib.asyncio import AsyncioProvider
    from HABApp.openhab.event_handler import OhEventHandler
    from HABApp.openhab.item_factory import OhItemFactory
    from HABApp.openhab.item_registry_handler import OhItemRegistryHandler


@contextlib.asynccontextmanager
async def _provide_watched_queue(asyncio_provider: AsyncioProvider,
                                 name: str) -> AsyncGenerator[WatchedSingleConsumerQueue, Any]:

    q: Final = WatchedSingleConsumerQueue()
    task: Final = asyncio_provider.create_task(
        q.queue_watcher_task(
            log=logging.getLogger('HABApp.openhab.queue'),
            name=name, sleep=asyncio_provider.sleep
        ),
        name=f'{name.title()}QueueWatcher'
    )
    yield q
    task.cancel()
    with contextlib.suppress(CancelledError):
        await task


@HABAPP_PROVIDER.register
async def provide_websocket_queue(asyncio_provider: AsyncioProvider) -> AsyncGenerator[OhWebsocketQueue, Any]:
    async with _provide_watched_queue(asyncio_provider, 'websocket') as q:
        yield q


@HABAPP_PROVIDER.register
async def provide_http_queue(asyncio_provider: AsyncioProvider) -> AsyncGenerator[OhHttpQueue, Any]:
    async with _provide_watched_queue(asyncio_provider, 'http') as q:
        yield q


@HABAPP_PROVIDER.register
async def provide_openhab_connection(
        connection_manager: ConnectionManager,
        asyncio_provider: AsyncioProvider,
) -> AsyncGenerator[OpenhabConnection, Any]:

    connection = OpenhabConnection(asyncio_provider)
    connection_manager.add(connection)

    yield connection

    connection.on_application_shutdown()


@HABAPP_PROVIDER.register
async def provide_client_session(app_config: ApplicationConfig,
                                 connection: OpenhabConnection) -> AsyncGenerator[OhClientSession, Any]:
    log: Final = connection.log
    config: Final = app_config.openhab.connection

    url: Final = config.url
    user: Final = config.user
    password: Final = config.password

    # do not run without an url
    if not url:
        msg: Final = 'Connection disabled (url missing)!'
        log.info(msg)
        connection.status_from_startup_to_disabled()
        yield Mock(OhClientSession, side_effect=RuntimeError(msg))
        return

    # do not run without user/pw - since OH3 mandatory
    is_token = user.startswith('oh.') or password.startswith('oh.')
    if not is_token and (not user or not password):
        msg: Final = 'Connection disabled (user/password missing)!'
        log.info(msg)
        connection.status_from_startup_to_disabled()
        yield Mock(OhClientSession, side_effect=RuntimeError(msg))
        return

    if not config.verify_ssl:
        log.info('Verify ssl set to False!')

    headers: Final = (('Authorization', aiohttp.encode_basic_auth(user, password)), )

    async with aiohttp.ClientSession(base_url=url, timeout=aiohttp.ClientTimeout(total=None),
                                     json_serialize=dump_json, headers=headers) as client:
        session = OhClientSession(session=client, ssl=config.verify_ssl, connection=connection)
        session.update_cfg(app_config.openhab.general)
        yield session


async def setup_openhab_connection(  # noqa: PLR0913
        connection: OpenhabConnection, config: ApplicationConfig,
        event_bus: EventBus, item_registry: ItemRegistry, asyncio_provider: AsyncioProvider,
        item_factory: OhItemFactory, registry_handler: OhItemRegistryHandler, event_handler: OhEventHandler,
        websocket_queue: OhWebsocketQueue, http_queue: OhHttpQueue, interface: OpenHabAsyncInterface,
        oh_connection: OhClientSession
) -> None:

    handler = ConnectionHandler(interface=interface, session=oh_connection)
    # config changes
    config.openhab.general.subscribe_for_changes(handler.update_cfg_general)

    connection.register_plugin(handler)

    connection.register_plugin(WaitForStartlevelPlugin(interface=interface), 0)
    connection.register_plugin(
        OutgoingCommandsPlugin(
            'OutgoingCommandsPlugin', asyncio_provider=asyncio_provider, http_queue=http_queue,
            oh_connection=oh_connection
        ),
        10
    )
    connection.register_plugin(
        LoadOpenhabItemsPlugin(
            'LoadItemsAndThings',
            item_factory=item_factory, registry_handler=registry_handler, item_registry=item_registry,
            interface=interface
        ),
        20
    )
    connection.register_plugin(
        WebsocketPlugin(
            event_handler=event_handler, asyncio_provider=asyncio_provider,
            ws_queue=websocket_queue, session=oh_connection, config=config.openhab
        ),
        30
    )
    connection.register_plugin(
        LoadOpenhabItemsPlugin(
            'SyncItemsAndThings',
            item_factory=item_factory, registry_handler=registry_handler, item_registry=item_registry,
            interface=interface
        ),
        40
    )
    connection.register_plugin(LoadTransformationsPlugin(interface=interface), 50)
    connection.register_plugin(
        PingPlugin(
            item_registry=item_registry, event_bus=event_bus,
            asyncio_provider=asyncio_provider, interface=interface
        ),
        100
    )
    connection.register_plugin(WaitForPersistenceRestore(item_registry=item_registry), 110)
    connection.register_plugin(ThingOverviewPlugin(interface=interface), 500_000)
    connection.register_plugin(BrokenLinksPlugin(item_registry=item_registry, interface=interface), 500_001)

    connection.register_plugin(ConnectionStateToEventBusPlugin(event_bus=event_bus))
    connection.register_plugin(AutoReconnectPlugin())
