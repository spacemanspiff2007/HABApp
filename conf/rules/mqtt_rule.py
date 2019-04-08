import datetime
import random
import time

import HABApp
from HABApp.core.events import ValueUpdateEvent


class MqttTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

        # do not print connection errors all the time if we are not connected
        # this is not required and only for convenience reasons in this repo
        testing = True
        if testing:
            try:
                self.mqtt.publish('test/test', 'Starting MqttTestRule')
            except ConnectionError as e:
                return

        self.run_every(
            datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=20),
            callback=self.publish_rand_value
        )

        self.listen_event('test/test', self.topic_changed)

    def publish_rand_value(self):
        print('test mqtt_publish')
        self.mqtt.publish('test/test', str(random.randint(0, 1000)))

    def topic_changed(self, event):
        assert isinstance(event, ValueUpdateEvent), type(event)
        print( f'mqtt topic "test/test" changed to {event.value}')

MqttTestRule()