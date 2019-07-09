import logging
import time

import HABApp
from HABApp.core.events import ValueUpdateEvent

log = logging.getLogger('HABApp.MqttTestEvents')


class TestMQTTEvents(HABApp.Rule):
    """This rule is testing MQTT by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.value_event = None

        self.run_in(2, self.run_tests)

    def run_tests(self):

        tests = {'test/topic': ['asdf', 1, 1.1, str({'a' : 'b'})]}

        for topic, values in tests.items():
            listener = self.listen_event(topic, self.mqtt_event, ValueUpdateEvent)

            for i, value_set in enumerate(values):
                if i:
                    item = self.get_item(topic)
                    assert isinstance(item, HABApp.mqtt.items.MqttItem)
                    item.publish(payload=value_set)
                else:
                    self.mqtt.publish(topic, value_set)

                start = time.time()
                timeout = False
                while value_set != self.value_event and not timeout:
                    if time.time() > start + 2:
                        timeout = True
                    time.sleep(0.01)

                if timeout:
                    log.error(f'Timeout testing {topic}: {value_set}')
                    continue

                log.info(f'Test of topic {topic}: {value_set} ok!')

            HABApp.core.EventBus.remove_listener(listener)

    def mqtt_event(self, event: ValueUpdateEvent):
        self.value_event = event.value


TestMQTTEvents()
