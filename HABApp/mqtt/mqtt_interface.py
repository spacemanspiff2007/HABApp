import typing
import ujson

import paho.mqtt.client as mqtt

from .mqtt_connection import MqttConnection, log
from ..config import Mqtt as MqttConfig


class MqttInterface:
    _RAISE_CONNECTION_ERRORS = True

    def __init__(self, connection: MqttConnection, config: MqttConfig):
        assert isinstance(connection, MqttConnection)
        assert isinstance(config, MqttConfig)

        self.__connection: MqttConnection = connection
        self.__config: MqttConfig = config

    def __is_connected(self) -> bool:
        if self.__connection.connected:
            return True

        if MqttInterface._RAISE_CONNECTION_ERRORS:
            raise ConnectionError('Mqtt client not connected')
        else:
            log.warning('Mqtt client not connected')
            return False

    def publish(self, topic: str, payload: typing.Any, qos: int = None, retain: bool = None) -> int:
        """
        Publish a value under a certain topic.
        If qos and/or retain is not set the value from the configuration file will be used.

        :param topic: MQTT topic
        :param payload: MQTT Payload
        :param qos: QoS, can be 0, 1 or 2. If not specified value from configuration file will be used.
        :param retain: retain message. If not specified value from configuration file will be used.
        :return: 0 if successful
        """

        assert isinstance(topic, str), type(topic)
        assert isinstance(qos, int) or qos is None, type(qos)
        assert isinstance(retain, bool) or retain is None, type(retain)

        if not self.__is_connected():
            return mqtt.MQTT_ERR_NO_CONN
        if self.__config.general.listen_only:
            return 100

        if qos is None:
            qos = self.__config.publish.qos
        if retain is None:
            retain = self.__config.publish.retain

        # convert these to string
        if isinstance(payload, (dict, list)):
            payload = ujson.dumps(payload)

        info = self.__connection.client.publish(topic, payload, qos, retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not publish to "{topic}": {mqtt.error_string(info.rc)}')
        return info

    def subscribe(self, topic: str, qos: int = None) -> int:
        """
        Subscribe to a MQTT topic. Subscriptions will be active until next disconnect

        :param topic: MQTT topic to subscribe to
        :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
        :return: 0 if successful
        """

        assert isinstance(topic, str), type(topic)
        assert isinstance(qos, int) or qos is None, type(qos)

        if not self.__is_connected():
            return mqtt.MQTT_ERR_NO_CONN

        # If no qos is specified load it from config
        if qos is None:
            qos = self.__config.subscribe.qos

        res, mid = self.__connection.client.subscribe(topic, qos)
        if res != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not subscribe to "{topic}": {mqtt.error_string(res)}')
        return res

    def unsubscribe(self, topic: str) -> int:
        """
        Unsubscribe from a MQTT topic

        :param topic: MQTT topic
        :return: 0 if successful
        """

        assert isinstance(topic, str), type(topic)

        if not self.__is_connected():
            return mqtt.MQTT_ERR_NO_CONN

        result, mid = self.__connection.client.unsubscribe(topic)
        if result != mqtt.MQTT_ERR_SUCCESS:
            log.error(f'Could not unsubscribe from "{topic}": {mqtt.error_string(result)}')
        return result


MQTT_INTERFACE: MqttInterface


def get_mqtt_interface(connection=None, config=None) -> MqttInterface:
    global MQTT_INTERFACE
    if connection is None:
        return MQTT_INTERFACE

    MQTT_INTERFACE = MqttInterface(connection, config)
    return MQTT_INTERFACE
