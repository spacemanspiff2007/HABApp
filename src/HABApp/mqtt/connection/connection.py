from __future__ import annotations

import logging
from typing import Optional

from aiomqtt import Client, MqttError

import HABApp
from HABApp.core.asyncio import async_context
from HABApp.core.connections import BaseConnection, Connections
from HABApp.core.connections.base_plugin import BaseConnectionPluginConnectedTask
from HABApp.core.const.const import PYTHON_310
from HABApp.core.wrapper import process_exception

log = logging.getLogger('HABApp.mqtt.connection')

if PYTHON_310:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

CONTEXT_TYPE: TypeAlias = Optional[Client]


def setup():
    config = HABApp.config.CONFIG.mqtt

    from HABApp.mqtt.connection.handler import CONNECTION_HANDLER
    from HABApp.mqtt.connection.subscribe import SUBSCRIPTION_HANDLER
    from HABApp.mqtt.connection.publish import PUBLISH_HANDLER

    connection = Connections.add(MqttConnection())

    connection.register_plugin(CONNECTION_HANDLER)
    connection.register_plugin(SUBSCRIPTION_HANDLER)
    connection.register_plugin(PUBLISH_HANDLER)

    # config changes
    config.subscribe.subscribe_for_changes(SUBSCRIPTION_HANDLER.subscription_cfg_changed)
    config.connection.subscribe_for_changes(connection.status_configuration_changed)


class MqttConnection(BaseConnection):
    def __init__(self):
        super().__init__('mqtt')
        self.context: CONTEXT_TYPE = None


class MqttPlugin(BaseConnectionPluginConnectedTask[MqttConnection]):

    def __init__(self, name: str, priority, task_name: str):
        super().__init__(name, priority, self._mqtt_wrap_task, task_name)

    async def mqtt_task(self):
        raise NotImplementedError()

    async def _mqtt_wrap_task(self):
        ctx = async_context.set('MQTT')

        connection = self.plugin_connection
        log = connection.log
        log.debug(f'{self.task.name} task start')

        try:
            await self.mqtt_task()
        except Exception as e:
            connection.set_error()
            if isinstance(e, MqttError):
                connection.log.error(e)
            else:
                process_exception(self.task.name, e, logger=log)
        finally:
            async_context.reset(ctx)
            log.debug(f'{self.task.name} task stop')
