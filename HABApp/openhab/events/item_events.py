import typing
import HABApp.core

from ..map_values import map_openhab_values
from .base_event import OpenhabEvent


class ItemStateEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):
    def __init__(self, name: str = '', value: typing.Any = None):
        super().__init__()

        # smarthome/items/NAME/state
        self.name: str = name
        self.value: typing.Any = value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/NAME/state
        return cls(topic[16:-6], map_openhab_values(payload['type'], payload['value']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemStateChangedEvent(OpenhabEvent, HABApp.core.events.ValueChangeEvent):
    def __init__(self, name: str = '', value: typing.Any = None, old_value: typing.Any = None):
        super().__init__()

        self.name: str = name
        self.value = value
        self.old_value = old_value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/Ping/statechanged
        return cls(
            topic[16:-13],
            map_openhab_values(payload['type'], payload['value']),
            map_openhab_values(payload['oldType'], payload['oldValue'])
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ItemCommandEvent(OpenhabEvent):
    def __init__(self, name: str = '', value: typing.Any = None):
        super().__init__()

        self.name: str = name
        self.value = value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/NAME/command
        return cls(topic[16:-8], map_openhab_values(payload['type'], payload['value']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemAddedEvent(OpenhabEvent):
    def __init__(self, name: str, type: str):
        super().__init__()

        self.name: str = name
        self.type: str = type

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # {'topic': 'smarthome/items/NAME/added'
        # 'payload': '{"type":"Contact","name":"Test","tags":[],"groupNames":[]}'
        # 'type': 'ItemAddedEvent'}
        return cls(payload['name'], payload['type'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}>'


class ItemUpdatedEvent(OpenhabEvent):
    def __init__(self, name: str, type: str):
        super().__init__()

        self.name: str = name
        self.type: str = type

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/NAME/updated
        # 'payload': '[{"type":"Switch","name":"Test","tags":[],"groupNames":[]},
        #              {"type":"Contact","name":"Test","tags":[],"groupNames":[]}]',
        # 'type': 'ItemUpdatedEvent'
        return cls(topic[16:-8], payload[1]['type'])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}>'


class ItemRemovedEvent(OpenhabEvent):
    def __init__(self, name: str = ''):
        super().__init__()

        self.name = name

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/Test/removed
        return cls(topic[16:-8])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}>'


class ItemStatePredictedEvent(OpenhabEvent):
    def __init__(self, name: str = '', value: typing.Any = None):
        super().__init__()

        # smarthome/items/NAME/state
        self.name: str = name
        self.value: typing.Any = value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'smarthome/items/NAME/statepredicted'
        return cls(topic[16:-15], map_openhab_values(payload['predictedType'], payload['predictedValue']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class GroupItemStateChangedEvent(OpenhabEvent):
    def __init__(self, name: str = '', item: str = '', value: typing.Any = None, old_value: typing.Any = None):
        super().__init__()

        self.name: str = name
        self.item: str = item

        self.value = value
        self.old_value = old_value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'smarthome/items/TestGroupAVG/TestNumber1/statechanged'
        parts = topic.split('/')

        return cls(
            parts[2], parts[3],
            map_openhab_values(payload['type'], payload['value']),
            map_openhab_values(payload['oldType'], payload['oldValue'])
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'
