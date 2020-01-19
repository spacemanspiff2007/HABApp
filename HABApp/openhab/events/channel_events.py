from .base_event import OpenhabEvent


class ChannelTriggeredEvent(OpenhabEvent):
    def __init__(self, _in_dict):
        super().__init__(_in_dict)

        # smarthome/items/NAME/state
        self.name: str = self._topic[19:-10]
        self.event: str = self._payload['event']
        self.channel: str = self._payload['channel']

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, event: {self.event}>'
