
import HABApp.core

from .base_event import BaseItemEvent


class ChannelTriggeredEvent(BaseItemEvent, HABApp.core.events.ValueUpdateEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/NAME/state
        self.name: str = self._topic[19:-10]
        self.event: str = self._payload['event']
        self.channel: str = self._payload['channel']

        # value wird gesetzt, weil wir von ValueUpdateEvent ableiten.
        # Todo: überlegen ob es nicht eine EventKlasse gibt
        self.value = self.event

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, event: {self.event}>'
