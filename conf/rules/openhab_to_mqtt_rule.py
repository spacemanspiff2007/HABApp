import HABApp
from HABApp.openhab.events import ItemStateEvent


class MyOpenhabToMQTTRule(HABApp.Rule):
    """This Rule mirrors all updates from openhab to MQTT"""

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

        self.listen_event( None, self.process_any_update, ItemStateEvent)

    def process_any_update(self, event):
        assert isinstance(event, ItemStateEvent)

        print( f'/openhab/{event.name} <- {event.value}')
        self.mqtt.publish( f'/openhab/{event.name}', event.value)

a = MyOpenhabToMQTTRule()

