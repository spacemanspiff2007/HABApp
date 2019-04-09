import paho.mqtt.client as mqtt

from .mqtt_connection import MqttConnection, log
from ..config import Mqtt as MqttConfig


class MqttInterface:
    def __init__(self, connection: MqttConnection, config: MqttConfig):
        assert isinstance(connection, MqttConnection)
        assert isinstance(config, MqttConfig)

        self.__connection: MqttConnection = connection
        self.__config: MqttConfig = config

    def publish(self, topic: str, payload, qos: int = None, retain: bool = None) -> int:
        """Publish a value under a certain topic.
        If qos and/or retain is not set it will be loaded from the configuration"""

        assert isinstance(topic, str), type(topic)
        assert isinstance(qos, int) or qos is None, type(qos)
        assert isinstance(retain, bool) or retain is None, type(retain)

        if not self.__connection.connected:
            raise ConnectionError(f'Mqtt client not connected')

        if qos is None:
            qos = self.__config.publish.qos
        if retain is None:
            retain = self.__config.publish.retain

        info = self.__connection.client.publish(topic, payload, qos, retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not publish to "{topic}": {mqtt.error_string(info.rc)}')
        return info

    def subscribe(self, topic: str, qos: int = None) -> int:
        """Subscribe to a MQTT topic until the next disconnect"""

        assert isinstance(topic, str), type(topic)
        assert isinstance(qos, int) or qos is None, type(qos)

        if not self.__connection.connected:
            raise ConnectionError(f'Mqtt client not connected')

        # If no qos is specified load it from config
        if qos is None:
            qos = self.__config.subscribe.qos

        res, mid = self.__connection.client.subscribe(topic, qos)
        if res != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not subscribe to "{topic}": {mqtt.error_string(res)}')
        return res

    def unsubscribe(self, topic: str) -> int:
        """Unsubscribe from a MQTT topic"""

        assert isinstance(topic, str), type(topic)

        if not self.__connection.connected:
            raise ConnectionError(f'Mqtt client not connected')

        result, mid = self.__connection.client.unsubscribe(topic)
        if result != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not unsubscribe from "{topic}": {mqtt.error_string(result)}')
        return result
