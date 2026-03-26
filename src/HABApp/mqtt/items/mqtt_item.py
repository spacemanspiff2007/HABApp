from typing import Any, Final, override

from HABApp.core.errors import ItemNameNotOfTypeStrError, ItemNotFoundException, WrongItemTypeError
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import BaseValueItem
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.mqtt import MqttInterface
from HABApp.mqtt.connection.interface import MqttUserPayload


class MqttBaseItem(BaseValueItem):

    def __init__(self, name: str, initial_value: Any = None, last_value: Any = None, *,
                 interface: MqttInterface, event_bus: EventBus) -> None:
        super().__init__(name, initial_value, last_value, event_bus=event_bus)
        self._mqtt_interface: Final = interface


class MqttItem(MqttBaseItem):
    """A simple item that represents a topic and a value"""

    @classmethod
    def get_create_item(cls, name: str, initial_value: Any = None, last_value: Any = None) -> 'MqttItem':
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :param last_value: last value the item will have if it gets created
        :return: item
        """
        if not isinstance(name, str):
            raise ItemNameNotOfTypeStrError.from_value(name)

        item_registry: Final = HABAPP_PROVIDER.get_existing(ItemRegistry)
        event_bus: Final = HABAPP_PROVIDER.get_existing(EventBus)

        try:
            item = item_registry.get_item(name)
        except ItemNotFoundException:
            item = cls(
                name, initial_value, last_value,
                event_bus=event_bus, interface=HABAPP_PROVIDER.get_existing(MqttInterface)
            )
            item_registry.add_item(item)

        if not isinstance(item, cls):
            raise WrongItemTypeError.from_item(item, cls)
        return item

    def publish(self, payload: MqttUserPayload, qos: int | None = None, retain: bool | None = None) -> None:
        """
        Publish the payload under the topic from the item.

        :param payload: MQTT Payload
        :param qos: QoS, can be ``0``, ``1`` or ``2``. If not specified value from configuration file will be used.
        :param retain: retain message. If not specified value from configuration file will be used.
        """

        self._mqtt_interface.publish(self.name, payload, qos=qos, retain=retain)

    @override
    def command_value(self, value: MqttUserPayload) -> None:
        """Send a command to the topic, the same as publish

        :param value: value to be sent
        """
        self._mqtt_interface.publish(self.name, value)
