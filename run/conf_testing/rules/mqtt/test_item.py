from HABAppTests import EventWaiter, ItemWaiter, TestBaseRule

from HABApp.core.events import ValueUpdateEventFilter
from HABApp.mqtt.events import MqttValueUpdateEventFilter
from HABApp.mqtt.items import MqttItem, MqttPairItem
from HABApp.mqtt.util import MqttPublishOptions


class TestMQTTEvents(TestBaseRule):
    """This rule is testing MQTT by posting values and checking the events"""

    def __init__(self) -> None:
        super().__init__()

        self.config.skip_on_failure = True

        self.mqtt_test_data = ['asdf', 1, 1.1, str({'a': 'b'}), {'key': 'value'}, ['mylist', 'mylistvalue']]

        self.add_test('MQTT events', self.test_mqtt_events, MqttValueUpdateEventFilter())
        self.add_test('MQTT ValueUpdate events', self.test_mqtt_events, ValueUpdateEventFilter())

        self.add_test('MQTT item publish', self.test_mqtt_item_publish)

        self.add_test('MQTT pair item', self.test_mqtt_pair_item)
        self.add_test('MQTT topic info', self.test_mqtt_topic_info)

    def test_mqtt_pair_item(self) -> None:
        topic_read = 'test/topic_read'
        topic_write = 'test/topic_write'

        item = MqttPairItem.get_create_item(topic_read, topic_write)

        # Ensure we send on the write topic
        with EventWaiter(topic_write, ValueUpdateEventFilter()) as event_waiter:
            item.publish('ddddddd')
            event_waiter.wait_for_event(value='ddddddd')

        # Read Topic has to be updated properly
        with ItemWaiter(item) as item_waiter:
            self.mqtt.publish(topic_read, 'asdfasdf')
            item_waiter.wait_for_state(item)

    def test_mqtt_events(self, event_type) -> None:
        topic = 'test/event_topic'
        with EventWaiter(topic, event_type) as waiter:
            for data in self.mqtt_test_data:
                self.mqtt.publish(topic, data)
                waiter.wait_for_event(value=data)

    def test_mqtt_item_publish(self) -> None:
        my_item = MqttItem.get_create_item('test/item_topic')
        with ItemWaiter(my_item) as waiter:
            for data in self.mqtt_test_data:
                my_item.publish(data)
                waiter.wait_for_state(data)

    def test_mqtt_topic_info(self) -> None:
        t = MqttPublishOptions('test/event_topic')
        with EventWaiter(t.topic, ValueUpdateEventFilter()) as waiter:
            t.publish('asdf')
            waiter.wait_for_event(value='asdf')


TestMQTTEvents()
