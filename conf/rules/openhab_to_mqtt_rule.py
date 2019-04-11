import HABApp
from HABApp.openhab.events import ItemStateEvent


class ExampleOpenhabToMQTTRule(HABApp.Rule):
    """This Rule mirrors all updates from openhab to MQTT"""

    def __init__(self):
        super().__init__()

        self.listen_event(None, self.process_any_update, ItemStateEvent)

    def process_any_update(self, event):
        assert isinstance(event, ItemStateEvent)

        print( f'/openhab/{event.name} <- {event.value}')
        self.mqtt.publish( f'/openhab/{event.name}', event.value)


ExampleOpenhabToMQTTRule()
