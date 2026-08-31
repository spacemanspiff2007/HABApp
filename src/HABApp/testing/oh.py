from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Final

from whenever import Instant

from HABApp.core.internals import EventBus, ItemRegistry, ItemRegistryItem
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import OpenHabValueType, RefreshTypeModel
from HABApp.openhab.events import ItemCommandEvent, ItemStateChangedEvent, ItemStateEvent
from HABApp.openhab.items import (
    CallItem,
    DatetimeItem,
    DimmerItem,
    ImageItem,
    LocationItem,
    NumberItem,
    OpenhabItem,
    PlayerItem,
    RollershutterItem,
    StringItem,
    SwitchItem,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SentOpenHABEvent:
    name: str
    value: Any
    source: str | None = None
    datetime: Instant = field(default_factory=Instant.now)


@dataclass(frozen=True, slots=True, kw_only=True)
class SentItemCommandEvent(SentOpenHABEvent):
    """A command that was sent to an openHAB item during a test"""


@dataclass(frozen=True, slots=True, kw_only=True)
class SentItemUpdateEvent(SentOpenHABEvent):
    """A state update that was posted for an openHAB item during a test"""


type SentItemEvent = SentItemCommandEvent | SentItemUpdateEvent


def _event_name(item: str | ItemRegistryItem) -> str:
    return item if isinstance(item, str) else item.name


class SentOhEventHistory:
    """Records all commands/updates that were sent to openHAB items during a test."""

    def __init__(self) -> None:
        self._events: Final[list[SentItemEvent]] = []

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[SentItemEvent]:
        return iter(self._events)

    def add(self, event: SentItemEvent) -> None:
        self._events.append(event)

    def clear(self) -> None:
        """Remove all recorded events"""
        self._events.clear()

    def commands(self, item: str | ItemRegistryItem | None = None) -> list[SentItemCommandEvent]:
        """Return all commands that were sent, optionally filtered by item"""
        name = None if item is None else _event_name(item)
        found: list[SentItemCommandEvent] = []
        for e in self._events:
            if isinstance(e, SentItemCommandEvent) and (name is None or e.name == name):
                found.append(e)
        return found

    def updates(self, item: str | ItemRegistryItem | None = None) -> list[SentItemUpdateEvent]:
        """Return all updates that were posted, optionally filtered by item"""
        name = None if item is None else _event_name(item)
        found: list[SentItemUpdateEvent] = []
        for e in self._events:
            if isinstance(e, SentItemUpdateEvent) and (name is None or e.name == name):
                found.append(e)
        return found

    def last_command(self, item: str | ItemRegistryItem) -> SentItemCommandEvent:
        """Return the last command that was sent to the given item"""
        if not (events := self.commands(item)):
            msg = f'No command was sent to "{_event_name(item)}"'
            raise AssertionError(msg)
        return events[-1]

    def last_update(self, item: str | ItemRegistryItem) -> SentItemUpdateEvent:
        """Return the last update that was posted for the given item"""
        if not (events := self.updates(item)):
            msg = f'No update was posted for "{_event_name(item)}"'
            raise AssertionError(msg)
        return events[-1]


def command_to_value(item: OpenhabItem, payload: OpenHabValueType, value: Any) -> Any:
    if value is None:
        return None

    if isinstance(payload, RefreshTypeModel):
        return item.value

    if isinstance(item, (CallItem, LocationItem, StringItem, NumberItem, PlayerItem, ImageItem, DatetimeItem)):
        return value

    if isinstance(item, SwitchItem) and value in ('ON', 'OFF'):
        return value

    if isinstance(item, DimmerItem):
        if isinstance(value, float):
            return value
        if value == 'ON':
            return 100
        if value == 'OFF':
            return 0
        if value == 'INCREASE':
            return min(item.value + 5, 100)
        if value == 'DECREASE':
            return max(item.value - 5, 0)

    if isinstance(item, RollershutterItem):
        if isinstance(value, float):
            return value
        if value == 'UP':
            return 0
        if value == 'DOWN':
            return 100
        if value == 'STOP':
            return item.value

    msg = f'Command {value} ({type(value)}) not implemented for {type(item)}'
    raise NotImplementedError(msg)


class OhWebsocketLoopbackQueue:
    def __init__(self, event_bus: EventBus, item_registry: ItemRegistry, history: SentOhEventHistory) -> None:
        self._event_bus: Final = event_bus
        self._item_registry: Final = item_registry
        self._history: Final = history

    def put_nowait(self, event: ItemStateSendEvent | ItemCommandSendEvent) -> None:
        _process_outgoing_event(
            event, item_registry=self._item_registry, event_bus=self._event_bus, history=self._history
        )
        return None


class OhHttpLoopbackQueue:
    def __init__(self, event_bus: EventBus, item_registry: ItemRegistry, history: SentOhEventHistory) -> None:
        self._event_bus: Final = event_bus
        self._item_registry: Final = item_registry
        self._history: Final = history

    def put_nowait(self, obj: tuple[str, Any, bool, str | None]) -> None:
        name, value, is_command, source = obj

        item: Final = self._item_registry.get_item(name)
        if not isinstance(item, OpenhabItem):
            msg = f'Item is not an openHAB item: {item}'
            raise TypeError(msg)

        if is_command:
            # noinspection protected-member
            event: Final = item._command_to_oh.create_event(item.name, value, source=source)
        else:
            # noinspection protected-member
            event: Final = item._update_to_oh.create_event(item.name, value, source=source)

        _process_outgoing_event(
            event, item_registry=self._item_registry, event_bus=self._event_bus, history=self._history
        )
        return None


def _process_outgoing_event(
        event: ItemStateSendEvent | ItemCommandSendEvent, *,
        item_registry: ItemRegistry, event_bus: EventBus, history: SentOhEventHistory) -> None:

    name: Final = event.topic.split('/')[-2]
    item: Final = item_registry.get_item(name)

    if not isinstance(item, OpenhabItem):
        msg = f'Item is not an openHAB item: {item}'
        raise TypeError(msg)

    value: Any = event.payload.get_value()
    is_command: Final = isinstance(event, ItemCommandSendEvent)

    if is_command:
        event_bus.post_event(name, ItemCommandEvent(name=name, value=value))
        value = command_to_value(item, event.payload, value)

    history.add(
        SentItemCommandEvent(name=name, value=value, source=event.source) if is_command else
        SentItemUpdateEvent(name=name, value=value, source=event.source)
    )

    old_value: Final = item.value
    changed = item.set_value(value)
    event_bus.post_event(name, ItemStateEvent(name=name, value=value))

    if changed:
        event_bus.post_event(
            name, ItemStateChangedEvent(
                name=name, value=value, old_value=old_value, last_state_update=None, last_state_change=None
            )
        )

    return None
