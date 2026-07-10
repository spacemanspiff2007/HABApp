from typing import Any, Final

from HABApp.core.internals import EventBus, ItemRegistry
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
    def __init__(self, event_bus: EventBus, item_registry: ItemRegistry) -> None:
        self._event_bus: Final = event_bus
        self._item_registry: Final = item_registry

    def put_nowait(self, event: ItemStateSendEvent | ItemCommandSendEvent) -> None:

        name: Final = event.topic.split('/')[-2]
        item: Final = self._item_registry.get_item(name)

        if not isinstance(item, OpenhabItem):
            msg = f'Item is not an openHAB item: {item}'
            raise TypeError(msg)

        value: Any = event.payload.get_value()

        if isinstance(event, ItemCommandSendEvent):
            self._event_bus.post_event(name, ItemCommandEvent(name=name, value=value))
            value = command_to_value(item, event.payload, value)

        old_value: Final = item.value
        changed = item.set_value(value)
        self._event_bus.post_event(name, ItemStateEvent(name=name, value=value))

        if changed:
            self._event_bus.post_event(name, ItemStateChangedEvent(name=name, value=value, old_value=old_value))

        return None
