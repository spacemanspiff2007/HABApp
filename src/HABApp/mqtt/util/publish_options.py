from __future__ import annotations

from typing import TYPE_CHECKING, Final, Self

from HABApp.core.const import MISSING, MISSING_TYPE


if TYPE_CHECKING:
    from HABApp.config.models.mqtt import QOS
    from HABApp.mqtt import MqttAsyncInterface, MqttInterface
    from HABApp.mqtt.connection.interface import MqttUserPayload


class MqttPublishOptions:
    """Allows to store the topic, qos and retain settings for a topic. These values can then be used to publish"""

    __slots__ = ('_interface', '_qos', '_retain', '_topic')

    def __init__(self, topic: str, *, qos: QOS | None, retain: bool | None,
                 interface: MqttInterface | MqttAsyncInterface) -> None:
        if not isinstance(topic, str):
            raise TypeError()
        if not topic:
            raise ValueError()

        self._interface: Final = interface
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

    def replace(self, topic: str | MISSING_TYPE = MISSING, *,
                qos: QOS | None | MISSING_TYPE = MISSING, retain: bool | None | MISSING_TYPE = MISSING) -> Self:
        """
        Replace the topic, qos and retain with the given values and return a new object.

        :param topic: New topic (if provided)
        :param qos: New qos (if provided)
        :param retain: New retain (if provided)
        :return: New object
        """

        return self.__class__(
            topic if topic is not MISSING else self._topic,
            qos=qos if qos is not MISSING else self._qos,
            retain=retain if retain is not MISSING else self._retain,
            interface=self._interface
        )

    def publish(self, payload: MqttUserPayload) -> None:
        """
        Publish a payload

        :param payload: MQTT Payload
        """

        self._interface.publish(self._topic, payload, qos=self._qos, retain=self._retain)
