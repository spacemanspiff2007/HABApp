from .base_event import OpenhabEvent


class ChannelTriggeredEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str event:
    :ivar str channel:
    """
    name: str
    event: str
    channel: str

    def __init__(self, name: str = '', event: str = '', channel: str = ''):
        super().__init__()

        self.name: str = name
        self.event: str = event
        self.channel: str = channel

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        return cls(topic[17:-10], payload['event'], payload['channel'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, event: {self.event}>'


class ChannelDescriptionChangedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str field:
    :ivar str value:
    """
    name: str
    field: str
    value: str

    def __init__(self, name: str = '', field: str = '', value: str = ''):
        super().__init__()

        self.name: str = name
        self.field: str = field
        self.value: str = value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        return cls(topic[17:-19], payload['field'], payload['value'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, field: {self.field}>'
