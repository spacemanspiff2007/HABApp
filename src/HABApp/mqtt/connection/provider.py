from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from aiomqtt import Client

from HABApp.core.connections import (
    AutoReconnectPlugin,
    ConnectionManager,
    ConnectionStateToEventBusPlugin,
)
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.mqtt.connection.connection import MqttConnection
from HABApp.mqtt.connection.handler import ConnectionHandler
from HABApp.mqtt.connection.interface import MqttAsyncInterface, MqttInterface
from HABApp.mqtt.connection.messages import MessagesHandler
from HABApp.mqtt.connection.publish import PublishHandler
from HABApp.mqtt.connection.subscribe import SubscriptionHandler


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from HABApp.config import ApplicationConfig


log = logging.getLogger('HABApp.mqtt.connection')


type MqttContextType = Client | None


@HABAPP_PROVIDER.register
async def setup(connection_manager: ConnectionManager, config: ApplicationConfig
                ) -> AsyncGenerator[tuple[MqttConnection, MqttAsyncInterface, MqttInterface], Any]:

    pub_cfg: Final = config.mqtt.general
    publish_handler: Final = PublishHandler(pub_cfg)
    pub_cfg.subscribe_for_changes(publish_handler.config_changed)

    sub_cfg: Final = config.mqtt.subscribe
    subscribe_handler: Final = SubscriptionHandler(sub_cfg)
    sub_cfg.subscribe_for_changes(subscribe_handler.config_changed)

    async_interface: Final = MqttAsyncInterface(config.mqtt, publish_handler.queue, subscribe_handler)
    sync_interface: Final = MqttInterface(async_interface)

    connection = connection_manager.add(MqttConnection())
    # config changes should trigger a reconnect
    config.mqtt.connection.subscribe_for_changes(connection.status_configuration_changed)

    connection.register_plugin(ConnectionHandler(), 0)
    connection.register_plugin(MessagesHandler(sync_interface), 10)
    connection.register_plugin(subscribe_handler, 20)
    connection.register_plugin(publish_handler, 30)

    connection.register_plugin(ConnectionStateToEventBusPlugin())
    connection.register_plugin(AutoReconnectPlugin())

    yield connection, async_interface, sync_interface

    connection.on_application_shutdown()


@HABAPP_PROVIDER.register
def _unpack_connection(objs: tuple[MqttConnection, MqttAsyncInterface, MqttInterface]) -> MqttConnection:
    return objs[0]


@HABAPP_PROVIDER.register
def _unpack_interface(objs: tuple[MqttConnection, MqttAsyncInterface, MqttInterface]) -> MqttAsyncInterface:
    return objs[1]


@HABAPP_PROVIDER.register
def _create_sync_interface(objs: tuple[MqttConnection, MqttAsyncInterface, MqttInterface]) -> MqttInterface:
    return objs[2]
