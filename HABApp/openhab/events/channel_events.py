from .base_event import OpenhabEvent


class ChannelTriggeredEvent(OpenhabEvent):
    def __init__(self, name: str = '', event: str = '', channel: str = ''):
        super().__init__()

        self.name: str = name
        self.event: str = event
        self.channel: str = channel

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        return cls(topic[19:-10], payload['event'], payload['channel'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, event: {self.event}>'
