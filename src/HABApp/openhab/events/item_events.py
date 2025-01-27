from typing import Any, Final

import HABApp.core

from .base_event import OpenhabEvent


class ItemStateEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemStateUpdatedEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemStateChangedEvent(OpenhabEvent, HABApp.core.events.ValueChangeEvent):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ItemCommandEvent(OpenhabEvent, HABApp.core.events.ValueCommandEvent):

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ItemAddedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar str | None label:
    :ivar frozenset[str] tags:
    :ivar frozenset[str] groups:
    """
    name: str
    type: str
    label: str | None
    tags: frozenset[str]
    groups: frozenset[str]

    def __init__(self, name: str, type: str, label: str | None,
                 tags: frozenset[str], group_names: frozenset[str]) -> None:
        super().__init__()

        self.name: str = name
        self.type: str = type
        self.label: str | None = label
        self.tags: frozenset[str] = tags
        self.groups: frozenset[str] = group_names

    def __repr__(self) -> str:
        tags = f' {{{", ".join(sorted(self.tags))}}}' if self.tags else ''
        grps = f' {{{", ".join(sorted(self.groups))}}}' if self.groups else ''
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}, tags:{tags}, groups:{grps}>'


class ItemUpdatedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar str | None label:
    :ivar frozenset[str] tags:
    :ivar frozenset[str] groups:
    """
    name: str
    type: str
    label: str | None
    tags: frozenset[str]
    groups: frozenset[str]

    def __init__(self, name: str, type: str, label: str | None,
                 tags: frozenset[str], group_names: frozenset[str]) -> None:
        super().__init__()

        self.name: str = name
        self.type: str = type
        self.label: str | None = label
        self.tags: frozenset[str] = tags
        self.groups: frozenset[str] = group_names

    def __repr__(self) -> str:
        tags = f' {{{", ".join(sorted(self.tags))}}}' if self.tags else ''
        grps = f' {{{", ".join(sorted(self.groups))}}}' if self.groups else ''
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}, tags:{tags}, groups:{grps}>'


class ItemRemovedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar str | None label:
    :ivar frozenset[str] tags:
    :ivar frozenset[str] groups:
    """
    name: str
    type: str
    label: str | None
    tags: frozenset[str]
    groups: frozenset[str]

    def __init__(self, name: str, type: str, label: str | None,
                 tags: frozenset[str], groups: frozenset[str]) -> None:
        super().__init__()

        self.name: str = name
        self.type: str = type
        self.label: str | None = label
        self.tags: frozenset[str] = tags
        self.groups: frozenset[str] = groups

    def __repr__(self) -> str:
        tags = f' {{{", ".join(sorted(self.tags))}}}' if self.tags else ''
        grps = f' {{{", ".join(sorted(self.groups))}}}' if self.groups else ''
        return f'<{self.__class__.__name__} name: {self.name}, type: {self.type}, tags:{tags}, groups:{grps}>'


class ItemStatePredictedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar Any value:
    """
    name: str
    value: Any

    def __init__(self, name: str, value: Any) -> None:
        super().__init__()
        self.name: Final = name
        self.value: Final = value

    def __repr__(self) -> str:
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

    def __init__(self, name: str, item: str, value: Any) -> None:
        super().__init__(name, value)
        self.item: Final = item

    def __repr__(self) -> str:
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

    def __init__(self, name: str, item: str, value: Any, old_value: Any) -> None:
        super().__init__(name, value, old_value)
        self.item: Final = item

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name: {self.name}, item: {self.item}, ' \
               f'value: {self.value}, old_value: {self.old_value}>'
