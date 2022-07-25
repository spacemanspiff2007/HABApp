from typing import Optional

from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import uses_item_registry
from HABApp.mqtt.mqtt_interface import publish
from . import MqttBaseItem

Items = uses_item_registry()


def build_write_topic(read_topic: str) -> Optional[str]:
    parts = read_topic.split('/')
    if parts[0] == 'zigbee2mqtt':
        parts.insert(-1, 'set')
        return '/'.join(parts)

    raise ValueError(f'Can not build write topic for "{read_topic}"')


class MqttPairItem(MqttBaseItem):
    """An item that represents both a topic that is used to read
    and a corresponding topic that is used to write values"""

    @classmethod
    def get_create_item(cls, name: str, write_topic: Optional[str] = None, initial_value=None) -> 'MqttPairItem':
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name.
        HABApp tries to automatically derive the write topic from the item name. In cases where this does not
        work it can be specified manually.

        :param name: item name (topic that reports the state)
        :param write_topic: topic that is used to write values or ``None`` (default) to build it automatically
        :param initial_value: state the item will have if it gets created
        :return: item
        """
        assert isinstance(name, str), type(name)

        # try to build write topic
        if write_topic is None:
            write_topic = build_write_topic(name)

        try:
            item = Items.get_item(name)
        except ItemNotFoundException:
            item = Items.add_item(cls(name, write_topic=write_topic, initial_value=initial_value))

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def __init__(self, name: str, initial_value=None, write_topic: str = None):
        super().__init__(name, initial_value)
        self.write_topic: str = write_topic

    def publish(self, payload, qos: int = None, retain: bool = None):
        """
        Publish the payload under the write topic from the item.

        :param payload: MQTT Payload
        :param qos: QoS, can be ``0``, ``1`` or ``2``. If not specified value from configuration file will be used.
        :param retain: retain message. If not specified value from configuration file will be used.
        :return: 0 if successful
        """

        return publish(self.write_topic, payload, qos=qos, retain=retain)
