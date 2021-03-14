.. _ref_mqtt:

MQTT
==================================

Interaction with the MQTT broker
---------------------------------
Interaction with the MQTT broker is done through the ``self.mqtt`` object in the rule or through
the :class:`~HABApp.mqtt.items.MqttItem`. When receiving a topic for the first time a new :class:`~HABApp.mqtt.items.MqttItem`
will automatically be created.

..  image:: /gifs/mqtt.gif



Rule Interface
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


Mqtt item types
------------------------------

Mqtt items have an additional publish method which make interaction with the mqtt broker easier.

.. execute_code::
    :hide_output:

    # hide
    import HABApp
    from unittest.mock import MagicMock
    HABApp.mqtt.items.mqtt_item.publish = MagicMock()
    # hide

    from HABApp.mqtt.items import MqttItem

    # items can be created manually or will be automatically
    # created when the first mqtt message is received
    my_mqtt_item = MqttItem.get_create_item('test/topic')

    # easy to publish values
    my_mqtt_item.publish('new_value')

    # comparing the item to get the state works, too
    if my_mqtt_item == 'test':
        pass # do something


MqttItem
""""""""""""""""""""""""""""""""""""""

.. inheritance-diagram:: HABApp.mqtt.items.MqttItem
   :parts: 1

.. autoclass:: HABApp.mqtt.items.MqttItem
   :members:
   :inherited-members:
   :member-order: groupwise

MqttPairItem
""""""""""""""""""""""""""""""""""""""
An item that consolidates a topic that reports states from a device and a topic that is used to write to a device.
It is created on the topic that reports the state from the device.

.. execute_code::
    :hide_output:

    # hide
    import HABApp
    from unittest.mock import MagicMock
    HABApp.mqtt.items.mqtt_pair_item.publish = MagicMock()
    # hide

    from HABApp.mqtt.items import MqttPairItem

    # MqttPairItem works out of the box with zigbee2mqtt
    mqtt = MqttPairItem.get_create_item("zigbee2mqtt/my_bulb/brightness")
    mqtt.publish("255")  # <-- will use the write topic

    # equivalent to
    mqtt = MqttPairItem.get_create_item("zigbee2mqtt/my_bulb/brightness", write_topic="zigbee2mqtt/my_bulb/set/brightness")


.. inheritance-diagram:: HABApp.mqtt.items.MqttPairItem
   :parts: 1

.. autoclass:: HABApp.mqtt.items.MqttPairItem
   :members:
   :inherited-members:
   :member-order: groupwise


Mqtt events
--------------------------------------


MqttValueUpdateEvent
""""""""""""""""""""""""""""""""""""""
Since this event inherits from :class:`~HABApp.core.events.ValueUpdateEvent` you can listen to :class:`~HABApp.core.events.ValueUpdateEvent`
and it will also trigger for :class:`~HABApp.openhab.events.ItemStateEvent`.

.. inheritance-diagram:: HABApp.mqtt.events.MqttValueUpdateEvent
   :parts: 1

.. autoclass:: HABApp.mqtt.events.MqttValueUpdateEvent
   :members:
   :inherited-members:
   :member-order: groupwise


MqttValueChangeEvent
""""""""""""""""""""""""""""""""""""""
Since this event inherits from :class:`~HABApp.core.events.ValueChangeEvent` you can listen to :class:`~HABApp.core.events.ValueChangeEvent`
and it will also trigger for :class:`~HABApp.mqtt.events.MqttValueUpdateEvent`.

.. inheritance-diagram:: HABApp.mqtt.events.MqttValueChangeEvent
   :parts: 1

.. autoclass:: HABApp.mqtt.events.MqttValueChangeEvent
   :members:
   :inherited-members:
   :member-order: groupwise



Example MQTT rule
--------------------------------------
.. literalinclude:: ../conf/rules/mqtt_rule.py
