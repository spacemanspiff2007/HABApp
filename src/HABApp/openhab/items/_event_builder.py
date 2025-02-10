from typing import Any, Final, override

from typing_extensions import Self

from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent, item_value_types
from HABApp.openhab.definitions.websockets.base import BaseOutEvent
from HABApp.openhab.definitions.websockets.item_value_types import ItemValueBase


class OutgoingEventBase:
    __slots__ = ('_event', '_name', '_types')

    def __init__(self, name: str, *types: str | type[ItemValueBase],
                 event: type[ItemCommandSendEvent | ItemStateSendEvent]) -> None:
        self._event: Final = event
        self._name: Final = name
        self._types: Final = tuple(self._check_type(t, check_existing=False) for t in types)

        if not issubclass(event, BaseOutEvent):
            msg = f'Expected {BaseOutEvent.__name__}, got {event}'
            raise TypeError(msg)

        if len(set(self._types)) != len(self._types):
            msg = 'Duplicate entries in types'
            raise ValueError(msg)

    def _check_type(self, other: Any, *, check_existing: bool = True) -> type[ItemValueBase]:
        if isinstance(other, str):
            suffix = 'TypeModel'
            available = {
                name.removesuffix(suffix): getattr(item_value_types, name)
                for name in dir(item_value_types) if name.endswith(suffix)
            }
            if (other := available.get(other)) is None:
                msg = f'Unknown type: {other}! Available: {", ".join(sorted(available))}'
                raise ValueError(msg)

        if not issubclass(other, ItemValueBase):
            msg = f'Expected ItemValueBase, got {other}'
            raise TypeError(msg)

        if check_existing and other in self._types:
            msg = f'{other.__name__} already in {self._name:s}'
            raise ValueError(msg)
        return other

    def __or__(self, other: type[ItemValueBase]) -> Self:
        to_add = self._check_type(other)
        return self.__class__(self._name, *self._types, to_add)

    def supported_event_names(self) -> tuple[str, ...]:
        return tuple(t.__name__ for t in self._types)

    def create_event(self, name: str, value: Any) -> BaseOutEvent:
        for t in self._types:
            if (r := t.from_value(value)) is not None:
                return self._event.create(name, r)

        if isinstance(value, ItemValueBase):
            return self._event.create(name, value)

        msg = f"Invalid value: '{value}' ({type(value)}) for {self._name:s}"
        raise ValueError(msg)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self._name:s}({", ".join(self.supported_event_names())})'


class OutgoingStateEvent(OutgoingEventBase):

    @override
    def __init__(self, name: str, *types: str | type[ItemValueBase]) -> None:
        super().__init__(name, *types, event=ItemStateSendEvent)


class OutgoingCommandEvent(OutgoingEventBase):
    @override
    def __init__(self, name: str, *types: str | type[ItemValueBase]) -> None:
        super().__init__(name, *types, event=ItemCommandSendEvent)
