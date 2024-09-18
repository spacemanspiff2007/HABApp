from __future__ import annotations

import logging
from typing import TypeAlias

from aiomqtt import Client, MqttError

import HABApp
from HABApp.core.asyncio import AsyncContext
from HABApp.core.connections import AutoReconnectPlugin, BaseConnection, Connections, ConnectionStateToEventBusPlugin
from HABApp.core.connections.base_connection import AlreadyHandledException
from HABApp.core.connections.base_plugin import BaseConnectionPluginConnectedTask


log = logging.getLogger('HABApp.mqtt.connection')


CONTEXT_TYPE: TypeAlias = Client | None


def setup():
    config = HABApp.config.CONFIG.mqtt

    from HABApp.mqtt.connection.handler import CONNECTION_HANDLER
    from HABApp.mqtt.connection.publish import PUBLISH_HANDLER
    from HABApp.mqtt.connection.subscribe import SUBSCRIPTION_HANDLER

    connection = Connections.add(CONNECTION)

    connection.register_plugin(CONNECTION_HANDLER, 0)
    connection.register_plugin(SUBSCRIPTION_HANDLER, 10)
    connection.register_plugin(PUBLISH_HANDLER, 20)

    connection.register_plugin(ConnectionStateToEventBusPlugin())
    connection.register_plugin(AutoReconnectPlugin())

    # config changes
    config.subscribe.subscribe_for_changes(SUBSCRIPTION_HANDLER.subscription_cfg_changed)
    config.connection.subscribe_for_changes(connection.status_configuration_changed)


class MqttConnection(BaseConnection):
    def __init__(self):
        super().__init__('mqtt')
        self.context: CONTEXT_TYPE = None

    def is_silent_exception(self, e: Exception):
        return isinstance(e, MqttError)


CONNECTION = MqttConnection()


class MqttPlugin(BaseConnectionPluginConnectedTask[MqttConnection]):

    def __init__(self, task_name: str):
        super().__init__(self._mqtt_wrap_task, task_name)

    async def mqtt_task(self):
        raise NotImplementedError()

    async def _mqtt_wrap_task(self):

        connection = self.plugin_connection
        log = connection.log
        log.debug(f'{self.task.name} task start')
        try:
            with AsyncContext('MQTT'), connection.handle_exception(self.mqtt_task):
                await self.mqtt_task()
        except AlreadyHandledException:
            pass
        finally:
            log.debug(f'{self.task.name} task finished')
