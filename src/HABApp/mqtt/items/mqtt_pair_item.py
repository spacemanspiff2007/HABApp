from typing import Any, Final

from HABApp.core.errors import ItemNameNotOfTypeStrError, ItemNotFoundException, WrongItemTypeError
from HABApp.core.internals import ItemRegistry
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.mqtt import MqttInterface
from HABApp.mqtt.connection.interface import MqttUserPayload
from HABApp.mqtt.items import MqttBaseItem


def build_write_topic(read_topic: str) -> str | None:
    parts = read_topic.split('/')
    if parts[0] == 'zigbee2mqtt':
        parts.insert(-1, 'set')
        return '/'.join(parts)

    msg = f'Can not build write topic for "{read_topic}"'
    raise ValueError(msg)


class MqttPairItem(MqttBaseItem):
    """An item that represents both a topic that is used to read
    and a corresponding topic that is used to write values"""

    @classmethod
    def get_create_item(cls, name: str, write_topic: str | None = None,
                        initial_value: Any = None, last_value: Any = None) -> 'MqttPairItem':
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name.
        HABApp tries to automatically derive the write topic from the item name. In cases where this does not
        work it can be specified manually.

        :param name: item name (topic that reports the state)
        :param write_topic: topic that is used to write values or ``None`` (default) to build it automatically
        :param initial_value: state the item will have if it gets created
        :return: item
        """
        if not isinstance(name, str):
            raise ItemNameNotOfTypeStrError.from_value(name)

        item_registry: Final = HABAPP_PROVIDER.get_existing(ItemRegistry)

        # try to build write topic
        if write_topic is None:
            write_topic = build_write_topic(name)

        try:
            item = item_registry.get_item(name)
        except ItemNotFoundException:
            item = item_registry.add_item(
                cls(
                    name, write_topic=write_topic, initial_value=initial_value, last_value=last_value,
                    interface=HABAPP_PROVIDER.get_existing(MqttInterface)
                )
            )

        if not isinstance(item, cls):
            raise WrongItemTypeError.from_item(item, cls)
        return item

    def __init__(self, name: str, initial_value: Any = None, last_value: Any = None,
                 write_topic: str | None = None, *, interface: MqttInterface) -> None:
        super().__init__(name, initial_value, last_value, interface=interface)
        self.write_topic: str = write_topic

    def publish(self, payload: MqttUserPayload, qos: int | None = None, retain: bool | None = None) -> None:
        """
        Publish the payload under the write topic from the item.

        :param payload: MQTT Payload
        :param qos: QoS, can be ``0``, ``1`` or ``2``. If not specified value from configuration file will be used.
        :param retain: retain message. If not specified value from configuration file will be used.
        :return: 0 if successful
        """

        self._mqtt_interface.publish(self.write_topic, payload, qos=qos, retain=retain)
