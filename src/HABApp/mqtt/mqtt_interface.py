import typing

import paho.mqtt.client as mqtt

import HABApp
from .mqtt_connection import STATUS, log
from ..core.const.json import dump_json


def __is_connected() -> bool:
    if STATUS.connected:
        return True
    raise ConnectionError('Mqtt client not connected')


def publish(topic: str, payload: typing.Any, qos: int = None, retain: bool = None) -> int:
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

    config = HABApp.config.CONFIG.mqtt

    if not __is_connected():
        return mqtt.MQTT_ERR_NO_CONN
    if config.general.listen_only:
        return 100

    if qos is None:
        qos = config.publish.qos
    if retain is None:
        retain = config.publish.retain

    # convert these to string
    if isinstance(payload, (dict, list)):
        payload = dump_json(payload)

    info = STATUS.client.publish(topic, payload, qos, retain)
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        log.error(f'Could not publish to "{topic}": {mqtt.error_string(info.rc)}')
    return info


def subscribe(topic: str, qos: int = None) -> int:
    """
    Subscribe to a MQTT topic. Note that subscriptions made this way are volatile and will only remain until
    the next disconnect.

    :param topic: MQTT topic to subscribe to
    :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
    :return: 0 if successful
    """

    assert isinstance(topic, str), type(topic)
    assert isinstance(qos, int) or qos is None, type(qos)

    if not __is_connected():
        return mqtt.MQTT_ERR_NO_CONN

    # If no qos is specified load it from config
    if qos is None:
        qos = HABApp.config.CONFIG.mqtt.subscribe.qos

    res, mid = STATUS.client.subscribe(topic, qos)
    if res != mqtt.MQTT_ERR_SUCCESS:
        log.error(f'Could not subscribe to "{topic}": {mqtt.error_string(res)}')
    return res


def unsubscribe(topic: str) -> int:
    """
    Unsubscribe from a MQTT topic

    :param topic: MQTT topic
    :return: 0 if successful
    """

    assert isinstance(topic, str), type(topic)

    if not __is_connected():
        return mqtt.MQTT_ERR_NO_CONN

    result, mid = STATUS.client.unsubscribe(topic)
    if result != mqtt.MQTT_ERR_SUCCESS:
        log.error(f'Could not unsubscribe from "{topic}": {mqtt.error_string(result)}')
    return result
