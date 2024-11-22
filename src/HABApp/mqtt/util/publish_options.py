from typing import Any, Final

from typing_extensions import Self

from HABApp.mqtt.interface_sync import publish


class MqttPublishOptions:
    """Allows to store the topic, qos and retain settings for a topic. These values can then be used to publish
    """
    def __init__(self, topic: str, qos: int | None = None, retain: bool | None = None) -> None:
        if not isinstance(topic, str):
            raise TypeError()
        if not topic:
            raise ValueError()

        self._topic: Final = topic
        self._qos: Final = qos
        self._retain: Final = retain

    @property
    def topic(self) -> str:
        """The topic"""
        return self._topic

    @property
    def qos(self) -> int | None:
        """QOS"""
        return self._qos

    @property
    def retain(self) -> bool | None:
        """Retain"""
        return self._retain

    def publish(self, payload: Any) -> None:
        """
        Publish a payload

        :param payload: MQTT Payload
        """

        return publish(self._topic, payload, qos=self._qos, retain=self._retain)

    def replace(self, topic: str | None = None, qos: int | None = None, retain: bool | None = None) -> Self:
        """
        Replace the topic, qos and retain with the given values and return a new object.

        :param topic: New topic (if provided)
        :param qos: New qos (if provided)
        :param retain: New retain (if provided)
        :return: New object
        """

        return self.__class__(
            topic if topic is not None else self._topic,
            qos if qos is not None else self._qos,
            retain if retain is not None else self._retain
        )
