.. HABApp documentation master file, created by
   sphinx-quickstart on Wed Apr 10 09:18:31 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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
