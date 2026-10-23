from typing import Any, Final, override

from whenever import Instant

import HABApp.core
from HABApp.openhab.types import EventSourceStr

from .base_event import OpenhabEvent


class ItemStateEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):

    __slots__ = ()

    @override
    def __repr__(self) -> str:
        value = f() if (f := getattr(value := self.value, '_value_str', None)) is not None else str(value)
        return f'<{self.__class__.__name__} name: {self.name}, value: {value}>'


class ItemStateUpdatedEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):
    """
    :ivar Instant | None last_state_update: Optional timestamp of the state update
    :ivar EventSourceStr | None source: Optional source of the update
    """
    __slots__ = ('last_state_update', 'source')

    last_state_update: Instant | None
    source: EventSourceStr | None

    def __init__(self, name: str, value: Any, *, last_state_update: Instant | None,
                 source: EventSourceStr | None = None) -> None:
        super().__init__(name, value)

        self.last_state_update: Final = last_state_update
        self.source: Final = source

    @override
    def __repr__(self) -> str:
        value = f() if (f := getattr(value := self.value, '_value_str', None)) is not None else str(value)
        return f'<{self.__class__.__name__} name: {self.name}, value: {value}>'


class ItemStateChangedEvent(OpenhabEvent, HABApp.core.events.ValueChangeEvent):
    """
    :ivar Instant | None last_state_update: Optional timestamp of the state update
    :ivar Instant | None last_state_change: Optional timestamp of the state change
    :ivar EventSourceStr | None source: Optional source of the update
    """

    __slots__ = ('last_state_change', 'last_state_update', 'source')

    last_state_update: Instant | None
    last_state_change: Instant | None
    source: EventSourceStr | None

    def __init__(self, name: str, value: Any, old_value: Any, *,
                 last_state_update: Instant | None, last_state_change: Instant | None,
                 source: EventSourceStr | None = None) -> None:
        super().__init__(name, value, old_value)

        self.last_state_update: Final = last_state_update
        self.last_state_change: Final = last_state_change
        self.source: Final = source

    @override
    def __repr__(self) -> str:
        value = f() if (f := getattr(value := self.value, '_value_str', None)) is not None else str(value)
        old_value = f() if (f := getattr(old_value := self.old_value, '_value_str', None)) is not None \
            else str(old_value)
        return f'<{self.__class__.__name__} name: {self.name}, value: {value}, old_value: {old_value}>'


class ItemCommandEvent(OpenhabEvent, HABApp.core.events.ValueCommandEvent):
    """
    :ivar EventSourceStr | None source: Optional source of the update
    """

    __slots__ = ('source', )

    source: EventSourceStr | None

    def __init__(self, name: str, value: Any, *, source: EventSourceStr | None = None) -> None:
        super().__init__(name, value)
        self.source: Final = source

    @override
    def __repr__(self) -> str:
        value = f() if (f := getattr(value := self.value, '_value_str', None)) is not None else str(value)
        return f'<{self.__class__.__name__} name: {self.name}, value: {value}>'


class ItemAddedEvent(OpenhabEvent):
    """
    :ivar str name:
    :ivar str type:
    :ivar str | None label:
    :ivar frozenset[str] tags:
    :ivar frozenset[str] groups:
    """

    __slots__ = ('groups', 'label', 'name', 'tags', 'type')

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

    __slots__ = ('groups', 'label', 'name', 'tags', 'type')

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

    __slots__ = ('groups', 'label', 'name', 'tags', 'type')

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
    :ivar bool is_confirmation:
    """

    __slots__ = ('is_confirmation', 'name', 'value')

    name: str
    value: Any
    is_confirmation: bool

    def __init__(self, name: str, value: Any, is_confirmation: bool) -> None:  # noqa: FBT001
        super().__init__()
        self.name: Final = name
        self.value: Final = value
        self.is_confirmation: Final = is_confirmation

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} name: {self.name}, value: {self.value} '
                f'is_confirmation: {self.is_confirmation}>')


class GroupStateUpdatedEvent(OpenhabEvent, HABApp.core.events.ValueUpdateEvent):
    """
    :ivar str name: Group name
    :ivar str item: Group item that caused the update
    :ivar Any value:
    """

    __slots__ = ('item', )

    name: str
    item: str
    value: Any

    def __init__(self, name: str, item: str, value: Any) -> None:
        super().__init__(name, value)
        self.item: Final = item

    @override
    def __repr__(self) -> str:
        value = f() if (f := getattr(value := self.value, '_value_str', None)) is not None else str(value)
        return f'<{self.__class__.__name__} name: {self.name}, item: {self.item}, value: {value}>'


class GroupStateChangedEvent(OpenhabEvent, HABApp.core.events.ValueChangeEvent):
    """
    :ivar str name:
    :ivar str item:
    :ivar Any value:
    :ivar Any old_value:
    """

    __slots__ = ('item', )

    name: str
    item: str
    value: Any
    old_value: Any

    def __init__(self, name: str, item: str, value: Any, old_value: Any) -> None:
        super().__init__(name, value, old_value)
        self.item: Final = item

    @override
    def __repr__(self) -> str:
        value = f() if (f := getattr(value := self.value, '_value_str', None)) is not None else str(value)
        old_value = f() if (f := getattr(old_value := self.old_value, '_value_str', None)) is not None \
            else str(old_value)
        return (f'<{self.__class__.__name__} name: {self.name}, '
                f'item: {self.item}, value: {value}, old_value: {old_value}>')
