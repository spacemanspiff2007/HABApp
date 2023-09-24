from asyncio import Queue
from typing import Optional, Union

from HABApp.config import CONFIG
from HABApp.config.models.mqtt import QOS
from HABApp.core.asyncio import run_func_from_async
from HABApp.core.const.json import dump_json
from HABApp.core.internals import ItemRegistryItem
from HABApp.mqtt.connection.connection import MqttPlugin


class PublishHandler(MqttPlugin):
    def __init__(self):
        super().__init__(task_name='MqttPublish')

    async def mqtt_task(self):
        connection = self.plugin_connection
        with connection.handle_exception(self.mqtt_task):
            client = self.plugin_connection.context
            assert client is not None

            cfg = CONFIG.mqtt.publish
            queue = QUEUE
            assert queue is not None

            # worker to publish things
            while True:
                topic, value, qos, retain = await queue.get()
                if qos is None:
                    qos = cfg.qos
                if retain is None:
                    retain = cfg.retain

                await client.publish(topic, value, qos, retain)
                queue.task_done()

    async def on_connected(self):
        global QUEUE

        QUEUE = Queue()
        await super().on_connected()

    async def on_disconnected(self):
        global QUEUE

        await super().on_disconnected()
        QUEUE = None


QUEUE: Optional[Queue] = Queue()


PUBLISH_HANDLER = PublishHandler()


def async_publish(topic: Union[str, ItemRegistryItem], payload, qos: Optional[QOS] = None,
                  retain: Optional[bool] = None):
    """
    Publish a value under a certain topic.
    If qos and/or retain is not set the value from the configuration file will be used.

    :param topic: MQTT topic or item
    :param payload: MQTT Payload
    :param qos: QoS, can be 0, 1 or 2. If not specified the value from configuration file will be used.
    :param retain: retain message. If not specified the value from configuration file will be used.
    """
    if (queue := QUEUE) is None:
        return None

    if isinstance(topic, ItemRegistryItem):
        topic = topic.name

    # convert these to string
    if isinstance(payload, (dict, list, set, frozenset)):
        payload = dump_json(payload)

    queue.put_nowait((topic, payload, qos, retain))


def publish(topic: Union[str, ItemRegistryItem], payload, qos: Optional[QOS] = None, retain: Optional[bool] = None):
    """
    Publish a value under a certain topic.
    If qos and/or retain is not set the value from the configuration file will be used.

    :param topic: MQTT topic or item
    :param payload: MQTT Payload
    :param qos: QoS, can be 0, 1 or 2. If not specified the value from configuration file will be used.
    :param retain: retain message. If not specified the value from configuration file will be used.
    """
    run_func_from_async(async_publish, topic, payload, qos, retain)
