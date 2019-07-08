.. _ref_mqtt:

MQTT
==================================

Interaction with a MQTT broker
------------------------------
Interaction with the MQTT broker is done through the ``self.mqtt`` object in the rule.

..  image:: /gifs/mqtt.gif



Function parameters
------------------------------
.. py:class:: mqtt
      
   .. py:method:: publish(topic: str, payload: typing.Any[, qos: int = None, retain: bool = None]) -> int
   
      Publish a value under a certain topic.
   
      :param topic: MQTT topic
      :param payload: MQTT Payload
      :param int qos: QoS, can be 0, 1 or 2. If not specified value from configuration file will be used.
      :param bool retain: retain message. If not specified value from configuration file will be used.
      :return: 0 if successful
   
   .. py:method:: subscribe(self, topic: str[, qos: int = None]) -> int
   
      Subscribe to a MQTT topic. Subscriptions will be active until next disconnect.
      For persistent subscriptions use the configuration file
   
      :param topic: MQTT topic to subscribe to
      :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
      :return: 0 if successful
   
   .. py:method:: unsubscribe(self, topic: str) -> int
   
      Unsubscribe from a MQTT topic
   
      :param topic: MQTT topic
      :return: 0 if successful


MQTT item types
------------------------------

Mqtt items have a publish method which make interaction with the mqtt broker easier.

Example::

    # items can be created manually or will be automatically created when the first mqtt message is received
    my_mqtt_item = self.create_item('test/topic', HABApp.mqtt.items.MqttItem)
    assert isinstance(my_mqtt_item, HABApp.mqtt.items.MqttItem)

    # easy publish
    my_mqtt_item.publish('new_value')

    # comparing the item to get the state works, too
    if my_mqtt_item == 'test':
        # do something

.. autoclass:: HABApp.mqtt.items.MqttItem
   :members:



Example MQTT rule
------------------
.. literalinclude:: ../conf/rules/mqtt_rule.py
