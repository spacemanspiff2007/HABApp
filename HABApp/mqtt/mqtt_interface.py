from .mqtt_connection import MqttConnection

class MqttInterface:
    def __init__(self, connection):
        self.__connection: MqttConnection = connection

    def publish(self, topic: str, payload, qos=None, retain=None):
        return self.__connection.publish(topic, payload, qos, retain)

    def subscribe(self, topic, qos=0):
        return self.__connection.subscribe(topic, qos)
