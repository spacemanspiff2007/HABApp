
.. module:: HABApp.mqtt

MQTT
==================================

Interaction in rules
------------------------
Interaction with the MQTT broker is done through the MqttInterface class which is available as self.mqtt::

    self.mqtt.publish
    self.mqtt.subscribe
    self.mqtt.unsubscribe
   
.. automethod:: MqttInterface.publish
.. automethod:: MqttInterface.subscribe
.. automethod:: MqttInterface.unsubscribe

Example MQTT rule
------------------
.. literalinclude:: ../conf/rules/mqtt_rule.py
