import logging
from typing import Final, override

from aiomqtt import Client, MqttError

from HABApp.core.connections import BaseConnection
from HABApp.core.connections.base_connection import AlreadyHandledException
from HABApp.core.connections.base_plugin import BaseConnectionPlugin, BaseConnectionPluginConnectedTask
from HABApp.core.lib.asyncio import AsyncioProvider


log: Final = logging.getLogger('HABApp.mqtt.connection')


type MqttContextType = Client | None


class MqttConnection(BaseConnection):
    def __init__(self, asyncio_provider: AsyncioProvider) -> None:
        super().__init__('mqtt', asyncio_provider=asyncio_provider)
        self.context: MqttContextType = None

    @override
    def is_silent_exception(self, e: Exception) -> bool:
        return isinstance(e, MqttError)


class MqttPlugin(BaseConnectionPlugin[MqttConnection]):
    pass


class MqttTaskPlugin(BaseConnectionPluginConnectedTask[MqttConnection]):

    def __init__(self, task_name: str, asyncio_provider: AsyncioProvider) -> None:
        super().__init__(self._mqtt_wrap_task, task_name=task_name, asyncio_provider=asyncio_provider)

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
