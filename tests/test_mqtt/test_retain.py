from HABApp.core import Items
from HABApp.mqtt.mqtt_connection import process_msg


class MqttDummyMsg:
    def __init__(self, topic='', payload='', retain=False):
        self.topic = topic
        self._topic = topic.encode('utf-8')
        self.payload = payload.encode('utf-8')
        self.retain = retain
        self.qos = 0


def test_retain_create():
    topic = '/test/creation'

    assert not Items.item_exists(topic)
    process_msg(None, None, MqttDummyMsg(topic, 'aaa', retain=False))
    assert not Items.item_exists(topic)

    # Retain True will create the item
    process_msg(None, None, MqttDummyMsg(topic, 'adsf123', retain=True))
    assert Items.item_exists(topic)
    assert Items.get_item(topic).value == 'adsf123'

    Items.pop_item(topic)
