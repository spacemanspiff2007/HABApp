from typing import Final

from aiomqtt.types import PayloadType

from HABApp.config.models.mqtt import General as GeneralMqttConfig
from HABApp.core.lib import SingleConsumerQueue
from HABApp.mqtt.connection.connection import MqttTaskPlugin


type MqttPublishQueueType = SingleConsumerQueue[tuple[str, PayloadType, int, bool]]


class PublishHandler(MqttTaskPlugin):
    def __init__(self, config: GeneralMqttConfig) -> None:
        super().__init__(task_name='MqttPublish')

        self._cfg: Final = config
        self.queue: Final[MqttPublishQueueType] = SingleConsumerQueue()

    def config_changed(self) -> None:
        self.queue.set_open(not self._cfg.listen_only)

    async def mqtt_task(self) -> None:

        with self.plugin_connection.handle_exception(self.mqtt_task):
            if (client := self.plugin_connection.context) is None:
                msg = 'No MQTT connection'
                raise RuntimeError(msg)

            queue: Final = self.queue

            # worker to publish things
            while True:
                topic, value, qos, retain = await queue.get()
                await client.publish(topic, value, qos, retain)

    async def on_connected(self) -> None:
        await super().on_connected()
        self.config_changed()

    async def on_disconnected(self) -> None:
        await super().on_disconnected()
        self.queue.set_open(False)
