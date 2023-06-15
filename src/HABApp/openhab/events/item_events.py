from typing import Any, FrozenSet, Optional, Final

import HABApp.core
from .base_event import OpenhabEvent
from ..map_values import map_openhab_values


class ItemStateEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/items/NAME/state
        return cls(topic[14:-6], map_openhab_values(payload['type'], payload['value']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemStateUpdatedEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/items/NAME/stateupdated
        return cls(topic[14:-13], map_openhab_values(payload['type'], payload['value']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemStateChangedEvent(OpenhabEvent, HABApp.core.events.ValueChangeEvent):

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/items/Ping/statechanged
        return cls(
            topic[14:-13],
            map_openhab_values(payload['type'], payload['value']),
            map_openhab_values(payload['oldType'], payload['oldValue'])
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ItemCommandEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar Any value:
    """
    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        super().__init__()

        self.name: str = name
        self.value: Any = value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/NAME/command
        return cls(topic[14:-8], map_openhab_values(payload['type'], payload['value']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemAddedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    """
    name: str
    type: str
    label: Optional[str]
    tags: FrozenSet[str]
    groups: FrozenSet[str]

    def __init__(self, name: str, type: str, label: Optional[str],
                 tags: FrozenSet[str], group_names: FrozenSet[str]):
        super().__init__()

        self.name: str = name
        self.type: str = type
        self.label: Optional[str] = label
        self.tags: FrozenSet[str] = tags
        self.groups: FrozenSet[str] = group_names

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # {'topic': 'openhab/items/NAME/added'
        # 'payload': '{"type":"Contact","name":"Test","tags":[],"groupNames":[]}'
        # 'type': 'ItemAddedEvent'}
        return cls(
            payload['name'], payload['type'], label=payload.get('label'),
            tags=frozenset(payload['tags']), group_names=frozenset(payload['groupNames'])
        )

    def __repr__(self):
        tags = f' {{{", ".join(sorted(self.tags))}}}' if self.tags else ""
        grps = f' {{{", ".join(sorted(self.groups))}}}' if self.groups else ""
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}, tags:{tags}, groups:{grps}>'


class ItemUpdatedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    """
    name: str
    type: str
    label: Optional[str]
    tags: FrozenSet[str]
    groups: FrozenSet[str]

    def __init__(self, name: str, type: str, label: Optional[str],
                 tags: FrozenSet[str], group_names: FrozenSet[str]):
        super().__init__()

        self.name: str = name
        self.type: str = type
        self.label: Optional[str] = label
        self.tags: FrozenSet[str] = tags
        self.groups: FrozenSet[str] = group_names

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/items/NAME/updated
        # 'payload': '[{"type":"Switch","name":"Test","tags":[],"groupNames":[]},
        #              {"type":"Contact","name":"Test","tags":[],"groupNames":[]}]',
        # 'type': 'ItemUpdatedEvent'
        new = payload[0]
        return cls(
            topic[14:-8], new['type'], label=new.get('label'),
            tags=frozenset(new['tags']), group_names=frozenset(new['groupNames'])
        )

    def __repr__(self):
        tags = f' {{{", ".join(sorted(self.tags))}}}' if self.tags else ""
        grps = f' {{{", ".join(sorted(self.groups))}}}' if self.groups else ""
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}, tags:{tags}, groups:{grps}>'


class ItemRemovedEvent(OpenhabEvent):
    """
    :ivar str name:
    """
    name: str

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # smarthome/items/Test/removed
        return cls(topic[14:-8])

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}>'


class ItemStatePredictedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar Any value:
    """
    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        super().__init__()
        self.name: Final = name
        self.value: Final = value

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'openhab/items/NAME/statepredicted'
        return cls(topic[14:-15], map_openhab_values(payload['predictedType'], payload['predictedValue']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class GroupStateUpdatedEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):
    """
    :ivar str name: Group name
    :ivar str item: Group item that caused the update
    :ivar Any value:
    """
    name: str
    item: str
    value: Any

    def __init__(self, name: str, item: str, value: Any):
        super().__init__(name, value)
        self.item: Final = item

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # openhab/items/GroupItem/ItemThatChanged/stateupdated
        parts = topic.split('/')
        return cls(parts[2], parts[3], map_openhab_values(payload['type'], payload['value']))

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, item: {self.item}, value: {self.value}>'


class GroupStateChangedEvent(OpenhabEvent, HABApp.core.events.ValueChangeEvent):
    """
    :ivar str name:
    :ivar str item:
    :ivar Any value:
    :ivar Any old_value:
    """
    name: str
    item: str
    value: Any
    old_value: Any

    def __init__(self, name: str, item: str, value: Any, old_value: Any):
        super().__init__(name, value, old_value)
        self.item: Final = item

    @classmethod
    def from_dict(cls, topic: str, payload: dict):
        # 'openhab/items/TestGroupAVG/TestNumber1/statechanged'
        parts = topic.split('/')

        return cls(
            parts[2], parts[3],
            map_openhab_values(payload['type'], payload['value']),
            map_openhab_values(payload['oldType'], payload['oldValue'])
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, item: {self.item}, ' \
               f'value: {self.value}, old_value: {self.old_value}>'
