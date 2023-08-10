from HABApp.core.internals import ItemRegistry
from HABApp.mqtt.connection.subscribe import msg_to_event


class MqttDummyMsg:
    def __init__(self, topic='', payload='', retain=False):
        self.topic = topic
        self._topic = topic.encode('utf-8')
        self.payload = payload.encode('utf-8')
        self.retain = retain
        self.qos = 0


async def test_retain_create(ir: ItemRegistry):
    topic = '/test/creation'

    assert not ir.item_exists(topic)
    await msg_to_event(topic, 'aaa', retain=False)
    assert not ir.item_exists(topic)

    # Retain True will create the item
    await msg_to_event(topic, 'adsf123', retain=True)
    assert ir.item_exists(topic)
    assert ir.get_item(topic).value == 'adsf123'
