import HABApp
from HABApp.openhab.events import ItemStateUpdatedEventFilter, ItemStateEvent
from HABApp.openhab.items import OpenhabItem


class ExampleOpenhabToMQTTRule(HABApp.Rule):
    """This Rule mirrors all updates from OpenHAB to MQTT"""

    def __init__(self):
        super().__init__()

        for item in self.get_items(OpenhabItem):
            item.listen_event(self.process_update, ItemStateUpdatedEventFilter())

    def process_update(self, event):
        assert isinstance(event, ItemStateEvent)

        print(f'/openhab/{event.name} <- {event.value}')
        self.mqtt.publish(f'/openhab/{event.name}', str(event.value))


ExampleOpenhabToMQTTRule()
