import HABApp.mqtt.mqtt_interface
from HABApp.core.items import Item


class MqttItem(Item):

    def publish(self, payload, qos=None, retain=None):
        """
        Publish the payload under the topic from the item.

        :param payload: MQTT Payload
        :param qos: QoS, can be 0, 1 or 2. If not specified value from configuration file will be used.
        :param retain: retain message. If not specified value from configuration file will be used.
        :return: 0 if successful
        """

        return HABApp.mqtt.mqtt_interface.MQTT_INTERFACE.publish(self.name, payload, qos=qos, retain=retain)
