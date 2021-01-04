import logging
import time

import HABApp
from HABApp.core.events import ValueUpdateEvent
from HABApp.mqtt.events import MqttValueUpdateEvent
from HABApp.mqtt.items import MqttItem
from HABAppTests import TestBaseRule, ItemWaiter, EventWaiter

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
        time.sleep(0.1)
        assert HABApp.core.Items.item_exists(topic) is True

        HABApp.core.Items.pop_item(topic)


TestMQTTEvents()
