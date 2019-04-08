import HABApp
from HABApp.openhab.events import ItemStateEvent

class MyOpenhabToMQTTRule(HABApp.Rule):

    def __init__(self):
        super().__init__()
        connected = True
        try:
            self.mqtt_publish('openhab/test', 'Starting MyOpenhabToMQTTRule')
        except ConnectionError as e:
            connected = False

        # do not print connection errors all the time if we are not connected
        if not connected:
            return None

        self.listen_event( None, self.process_any_update, ItemStateEvent)

    def process_any_update(self, event):
        assert isinstance(event, ItemStateEvent)
        print( f'/openhab/{event.name} <- {event.value}')
        self.mqtt_publish( f'/openhab/{event.name}', event.value)

a = MyOpenhabToMQTTRule()

