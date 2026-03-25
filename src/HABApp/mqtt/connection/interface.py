from collections.abc import Iterable
from typing import Final

from pydantic import BaseModel

from HABApp.config.models.mqtt import QOS, MqttConfig
from HABApp.core.asyncio import run_func_from_async
from HABApp.core.const.json import dump_json
from HABApp.core.internals import ItemRegistryItem
from HABApp.mqtt.connection.publish import MqttPublishQueueType
from HABApp.mqtt.connection.subscribe import SubscriptionHandler


type MqttUserPayload = (
    str | bytes | bytearray | int | float | None |
    BaseModel | dict | list | set | frozenset
)


class MqttAsyncInterface:
    __slots__ = ('_config_pub', '_pub_queue', '_sub_handler')

    def __init__(self, config: MqttConfig, publish_queue: MqttPublishQueueType,
                 subscription_handler: SubscriptionHandler) -> None:

        self._pub_queue: Final = publish_queue
        self._config_pub: Final = config.publish
        self._sub_handler: Final = subscription_handler

    def publish(self, topic: str | ItemRegistryItem, payload: MqttUserPayload, *,
                qos: QOS | None = None, retain: bool | None = None) -> None:
        """
        Publish a value under a certain topic.
        If qos and/or retain is not set the value from the configuration file will be used.

        :param topic: MQTT topic or item
        :param payload: MQTT Payload
        :param qos: QoS, can be 0, 1 or 2. If not specified the value from configuration file will be used.
        :param retain: retain message. If not specified the value from configuration file will be used.
        """
        if isinstance(topic, ItemRegistryItem):
            topic = topic.name

        data: MqttUserPayload

        if not isinstance(payload, (str, bytes, bytearray, int, float)):
            if isinstance(payload, BaseModel):
                data = payload.model_dump_json()
            elif isinstance(payload, (dict, list, set, frozenset)):
                data = dump_json(payload)
            elif payload is None:
                data = payload
            else:
                msg = f'Payload must be of type str, bytes, bytearray, int, float or None, got {type(payload).__name__}'
                raise TypeError(msg)
        else:
            data = payload

        if qos is None:
            qos = self._config_pub.qos
        if retain is None:
            retain = self._config_pub.retain

        self._pub_queue.put_nowait((topic, data, qos, retain))
        return None

    def subscribe(self, topic_or_topics: str | Iterable[str] | Iterable[tuple[str, int | None]], *,
                  qos: QOS | None = None) -> None:
        """
        Subscribe to a MQTT topic. Note that subscriptions made this way are volatile and will only remain until
        the next restart.

        :param topic_or_topics: MQTT topic or multiple topic qos pairs to subscribe to
        :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
        """
        topics: tuple[tuple[str, QOS | None], ...]

        if isinstance(topic_or_topics, str):
            topics = ((topic_or_topics, None), )
        else:
            objs: list[tuple[str, QOS | None]] = []
            for obj in topic_or_topics:
                if isinstance(obj, str):
                    objs.append((obj, qos))
                    continue

                if isinstance(obj, tuple):
                    topic, qos = obj
                    if isinstance(topic, str) and isinstance(qos, int) and 0 <= qos <= 2:
                        objs.append((topic, qos))

                msg = f'Invalid topic or qos pair: {obj}'
                raise TypeError(msg)

            topics = tuple(objs)

        self._sub_handler.subscribe(topics)

    def unsubscribe(self, topic_or_topics: str | Iterable[str]) -> None:
        """
        Unsubscribe from a MQTT topic

        :param topic_or_topics: MQTT topic
        """
        topics: tuple[str, ...] = (topic_or_topics, ) if isinstance(topic_or_topics, str) else tuple(topic_or_topics)
        self._sub_handler.unsubscribe(topics)


class MqttInterface:
    __slots__ = ('_i',)

    def __init__(self, async_interface: MqttAsyncInterface) -> None:
        self._i: Final = async_interface

    def publish(self, topic: str | ItemRegistryItem, payload: MqttUserPayload, *,
                qos: QOS | None = None, retain: bool | None = None) -> None:
        """
        Publish a value under a certain topic.
        If qos and/or retain is not set the value from the configuration file will be used.

        :param topic: MQTT topic or item
        :param payload: MQTT Payload
        :param qos: QoS, can be 0, 1 or 2. If not specified the value from configuration file will be used.
        :param retain: retain message. If not specified the value from configuration file will be used.
        """
        return run_func_from_async(self._i.publish, topic, payload, qos=qos, retain=retain)

    def subscribe(self, topic_or_topics: str | Iterable[str] | Iterable[tuple[str, int | None]], *,
                  qos: QOS | None = None) -> None:
        """
        Subscribe to a MQTT topic. Note that subscriptions made this way are volatile and will only remain until
        the next restart.

        :param topic_or_topics: MQTT topic or multiple topic qos pairs to subscribe to
        :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
        """
        return run_func_from_async(self._i.subscribe, topic_or_topics, qos=qos)

    def unsubscribe(self, topic_or_topics: str | Iterable[str]) -> None:
        """
        Unsubscribe from a MQTT topic

        :param topic_or_topics: MQTT topic
        """
        return run_func_from_async(self._i.unsubscribe, topic_or_topics)
