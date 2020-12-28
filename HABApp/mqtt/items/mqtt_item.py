import HABApp.mqtt.mqtt_interface
from HABApp.core.items import BaseValueItem


class MqttBaseItem(BaseValueItem):
    pass


class MqttItem(MqttBaseItem):
    """A simple item that represents a topic and a value"""

    @classmethod
    def get_create_item(cls, name: str, initial_value=None) -> 'MqttItem':
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :return: item
        """
        assert isinstance(name, str), type(name)

        try:
            item = HABApp.core.Items.get_item(name)
        except HABApp.core.Items.ItemNotFoundException:
            item = cls(name, initial_value)
            HABApp.core.Items.add_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item

    def publish(self, payload, qos: int = None, retain: bool = None):
        """
        Publish the payload under the topic from the item.

        :param payload: MQTT Payload
        :param qos: QoS, can be ``0``, ``1`` or ``2``. If not specified value from configuration file will be used.
        :param retain: retain message. If not specified value from configuration file will be used.
        :return: 0 if successful
        """

        return HABApp.mqtt.mqtt_interface.MQTT_INTERFACE.publish(self.name, payload, qos=qos, retain=retain)
