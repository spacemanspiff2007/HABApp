
.. module:: HABApp.mqtt

MQTT
==================================

Interaction with a MQTT broker
------------------------------
Interaction with the MQTT broker is done through the :py:attr:`self.mqtt` object in the rule.

..  image:: /gifs/mqtt.gif



Function parameters
------------------------------
..  py:function:: self.mqtt.publish(topic: str, payload: typing.Any[, qos: int = None, retain: bool = None]) -> int

    Publish a value under a certain topic.

    :param topic: MQTT topic
    :param payload: MQTT Payload
    :param int qos: QoS, can be 0, 1 or 2. If not specified value from configuration file will be used.
    :param bool retain: retain message. If not specified value from configuration file will be used.
    :return: 0 if successful

..  py:function:: self.mqtt.subscribe(self, topic: str[, qos: int = None]) -> int

    Subscribe to a MQTT topic. Subscriptions will be active until next disconnect.
    For persistent subscriptions use the configuration file

    :param topic: MQTT topic to subscribe to
    :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
    :return: 0 if successful

..  py:function:: self.mqtt.unsubscribe(self, topic: str) -> int

    Unsubscribe from a MQTT topic

    :param topic: MQTT topic
    :return: 0 if successful


Example MQTT rule
------------------
.. literalinclude:: ../conf/rules/mqtt_rule.py
