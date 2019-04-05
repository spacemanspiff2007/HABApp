import datetime
import random
import time

import HABApp
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent, AllEvents
from HABApp.openhab.events import ItemStateEvent


class MqttTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()
        connected = True

        try:
            self.mqtt_publish('test/test', 'Starting MqttTestRule')
        except ConnectionError as e:
            connected = False

        # do not print connection erros all the time if we are not connected
        if not connected:
            return None

        self.run_every(
            datetime.datetime.now() + datetime.timedelta(seconds=10),
            interval=datetime.timedelta(seconds=20),
            callback=self.publish_rand_value
        )

        self.listen_event('test/test', self.topic_changed)

    def publish_rand_value(self):
        print('test mqtt_publish')
        self.mqtt_publish('test/test', str(random.randint(0, 1000)))

    def topic_changed(self, event):
        assert isinstance(event, ValueUpdateEvent), type(event)
        print( f'mqtt topic "test/test" changed to {event.value}')

MqttTestRule()



class NameSuggestionTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()

NameSuggestionTestRule()
NameSuggestionTestRule()



class MyOwnNameTestRule(HABApp.Rule):
    def __init__(self):
        super().__init__()
        self.rule_name='MyOwnRuleName'

MyOwnNameTestRule()



class MyRule(HABApp.Rule):

    def __init__(self):
        super().__init__()
        self.listen_event( 'TestSwitchTOGGLE', self.cb, ItemStateEvent)
        self.listen_event( 'TestContactTOGGLE', self.cb, ItemStateEvent)
        self.listen_event( 'TestDateTimeTOGGLE', self.cb, ItemStateEvent)

        self.run_on_day_of_week( datetime.time(14,34,20), ['Mo'], self.cb, 'run_on_day_of_week')

        self.run_every(datetime.datetime.now() + datetime.timedelta(seconds=5), 1, self.print_ts, 'Sec P1', asdf='P2')

        self.listen_event('', self.process_any_update, ValueUpdateEvent)

    def print_ts(self, arg, asdf = None):
        print( f'{time.time():.3f} : {arg}, {asdf}')
        self.post_update('TestDateTime9', datetime.datetime.now())


    def cb(self, event):
        print( f'CALLBACK: {event}')
        assert isinstance(event, ValueUpdateEvent)
        #time.sleep(0.6)

        # s = time.time()
        #
        # for k in range(100):
        #     self.send_Command('TestString9', f"{k}")
        #
        # self.post_Update('TestString8', "11")
        # print( f'dauer: {time.time() - s}')

    def process_any_update(self, event):
        print(f'on_any_event: {event}')


a = MyRule()







