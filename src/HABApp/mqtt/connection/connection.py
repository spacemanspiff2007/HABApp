from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypeAlias

from aiomqtt import Client, MqttError

from HABApp.core.connections import (
    AutoReconnectPlugin,
    BaseConnection,
    ConnectionManager,
    ConnectionStateToEventBusPlugin,
)
from HABApp.core.connections.base_connection import AlreadyHandledException
from HABApp.core.connections.base_plugin import BaseConnectionPluginConnectedTask
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from HABApp.config import ApplicationConfig


log = logging.getLogger('HABApp.mqtt.connection')


CONTEXT_TYPE: TypeAlias = Client | None


@HABAPP_PROVIDER.register
async def setup(connection_manager: ConnectionManager, config: ApplicationConfig) -> AsyncGenerator[
    MqttConnection, Any]:

    from HABApp.mqtt.connection.handler import CONNECTION_HANDLER
    from HABApp.mqtt.connection.publish import PUBLISH_HANDLER
    from HABApp.mqtt.connection.subscribe import SUBSCRIPTION_HANDLER

    connection = connection_manager.add(CONNECTION)

    connection.register_plugin(CONNECTION_HANDLER, 0)
    connection.register_plugin(SUBSCRIPTION_HANDLER, 10)
    connection.register_plugin(PUBLISH_HANDLER, 20)

    connection.register_plugin(ConnectionStateToEventBusPlugin())
    connection.register_plugin(AutoReconnectPlugin())

    # config changes
    config.mqtt.subscribe.subscribe_for_changes(SUBSCRIPTION_HANDLER.subscription_cfg_changed)
    config.mqtt.connection.subscribe_for_changes(connection.status_configuration_changed)

    yield connection

    connection.on_application_shutdown()



class MqttConnection(BaseConnection):
    def __init__(self) -> None:
        super().__init__('mqtt')
        self.context: CONTEXT_TYPE = None

    def is_silent_exception(self, e: Exception):
        return isinstance(e, MqttError)


CONNECTION = MqttConnection()


class MqttPlugin(BaseConnectionPluginConnectedTask[MqttConnection]):

    def __init__(self, task_name: str) -> None:
        super().__init__(self._mqtt_wrap_task, task_name)

    async def mqtt_task(self):
        raise NotImplementedError()

    async def _mqtt_wrap_task(self) -> None:

        connection = self.plugin_connection
        log = connection.log
        log.debug(f'{self.task.name} task start')
        try:
            with connection.handle_exception(self.mqtt_task):
                await self.mqtt_task()
        except AlreadyHandledException:
            pass
        finally:
            log.debug(f'{self.task.name} task finished')
