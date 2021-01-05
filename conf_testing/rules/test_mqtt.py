import logging
import time

import HABApp
from HABApp.core.events import ValueUpdateEvent
from HABApp.mqtt.events import MqttValueUpdateEvent
from HABApp.mqtt.items import MqttItem, MqttPairItem
from HABApp.mqtt.mqtt_connection import connect, disconnect
from HABAppTests import EventWaiter, ItemWaiter, TestBaseRule

log = logging.getLogger('HABApp.MqttTestEvents')


class TestMQTTEvents(TestBaseRule):
    """This rule is testing MQTT by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.config.skip_on_failure = True

        self.mqtt_test_data = ['asdf', 1, 1.1, str({'a': 'b'}), {'key': 'value'}, ['mylist', 'mylistvalue']]

        self.add_test('MQTT events', self.test_mqtt_events, MqttValueUpdateEvent)
        self.add_test('MQTT ValueUpdate events', self.test_mqtt_events, ValueUpdateEvent)

        self.add_test('MQTT item update', self.test_mqtt_state)

        self.add_test('MQTT item creation', self.test_mqtt_item_creation)
        self.add_test('MQTT pair item', self.test_mqtt_pair_item)

    def test_mqtt_pair_item(self):
        topic_read = 'test/topic_read'
        topic_write = 'test/topic_write'
    
        item = MqttPairItem.get_create_item(topic_read, topic_write)
        
        # Ensure we send on the write topic
        with EventWaiter(topic_write, ValueUpdateEvent) as event_waiter:
            item.publish('ddddddd')
            event_waiter.wait_for_event('ddddddd')

        # Read Topic has to be updated properly
        with ItemWaiter(item) as item_waiter:
            self.mqtt.publish(topic_read, 'asdfasdf')
            item_waiter.wait_for_state(item)

        return event_waiter.events_ok and item_waiter.states_ok

    def test_mqtt_events(self, event_type):
        topic = 'test/event_topic'
        with EventWaiter(topic, event_type) as waiter:
            for data in self.mqtt_test_data:
                self.mqtt.publish(topic, data)
                waiter.wait_for_event(data)

        return waiter.events_ok

    def test_mqtt_state(self):
        my_item = MqttItem.get_create_item('test/item_topic')
        with ItemWaiter(my_item) as waiter:
            for data in self.mqtt_test_data:
                my_item.publish(data)
                waiter.wait_for_state(data)

        return waiter.states_ok

    def test_mqtt_item_creation(self):
        topic = 'mqtt/item/creation'
        assert HABApp.core.Items.item_exists(topic) is False

        assert self.mqtt.publish(topic, 'asdf')
        time.sleep(0.1)
        assert HABApp.core.Items.item_exists(topic) is False

        # We create the item only on retain
        assert self.mqtt.publish(topic, 'asdf', retain=True)
        
        # We need to reconnect to receive the message
        disconnect()
        connect()

        time.sleep(0.1)
        assert HABApp.core.Items.item_exists(topic) is True

        HABApp.core.Items.pop_item(topic)


TestMQTTEvents()
