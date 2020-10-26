from .base_event import OpenhabEvent

# smarthome/channels/NAME/triggered -> 19
# openhab/channels/NAME/triggered   -> 17
# todo: revert this once we go OH3 only
NAME_START: int = 17


class ChannelTriggeredEvent(OpenhabEvent):
    def __init__(self, name: str = '', event: str = '', channel: str = ''):
        super().__init__()

        self.name: str = name
        self.event: str = event
        self.channel: str = channel

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        return cls(topic[NAME_START:-10], payload['event'], payload['channel'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, event: {self.event}>'
