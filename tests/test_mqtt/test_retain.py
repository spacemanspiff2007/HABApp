from HABApp.core.internals import TYPE_ITEM_REGISTRY
from HABApp.mqtt.mqtt_connection import process_msg


class MqttDummyMsg:
    def __init__(self, topic='', payload='', retain=False):
        self.topic = topic
        self._topic = topic.encode('utf-8')
        self.payload = payload.encode('utf-8')
        self.retain = retain
        self.qos = 0


def test_retain_create(ir: TYPE_ITEM_REGISTRY):
    topic = '/test/creation'

    assert not ir.item_exists(topic)
    process_msg(None, None, MqttDummyMsg(topic, 'aaa', retain=False))
    assert not ir.item_exists(topic)

    # Retain True will create the item
    process_msg(None, None, MqttDummyMsg(topic, 'adsf123', retain=True))
    assert ir.item_exists(topic)
    assert ir.get_item(topic).value == 'adsf123'
