from inspect import isclass
from typing import Any, Final, Literal, NotRequired, Self, TypedDict, overload

from HABApp.core.internals import EventBus
from HABApp.core.items import BaseItem, Item
from HABApp.mqtt import MqttInterface
from HABApp.mqtt.items import MqttBaseItem, MqttItem, MqttPairItem
from HABApp.openhab.connection.handler import OpenHabSyncInterface
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.openhab.items import (
    CallItem,
    ColorItem,
    ContactItem,
    DatetimeItem,
    DimmerItem,
    GroupItem,
    ImageItem,
    LocationItem,
    NumberItem,
    OpenhabItem,
    PlayerItem,
    RollershutterItem,
    StringItem,
    SwitchItem,
)


class MetadataDict(TypedDict):
    value: NotRequired[str | int | bool | float]
    config: NotRequired[dict[str, Any]]


type OhGroupType = list[str] | tuple[str, ...] | set[str] | frozenset[str]


type OhItemTypeLiteral = Literal[
    'String', 'StringItem', 'Number', 'NumberItem', 'Switch', 'SwitchItem', 'Contact', 'ContactItem',
    'Rollershutter', 'RollershutterItem', 'Dimmer', 'DimmerItem', 'Datetime', 'DatetimeItem',
    'Color', 'ColorItem', 'Image', 'ImageItem', 'Group', 'GroupItem', 'Player', 'PlayerItem',
    'Location', 'LocationItem', 'Call', 'CallItem'
]


class TestingItems:
    def __init__(self) -> None:
        self._items: Final[list[dict[str, Any]]] = []

    @overload
    def add(self, type: Literal['Item'] | type[Item], name: str, value: Any = None, *,
            last_value: Any = None) -> Self: ...

    @overload
    def add(self, type: Literal['MqttItem', 'Mqtt'] | type[MqttItem], name: str, value: Any = None, *,
            last_value: Any = None) -> Self: ...

    @overload
    def add(self, type: Literal['MqttPairItem', 'MqttPair'] | type[MqttPairItem], name: str, value: Any = None, *,
            last_value: Any = None, write_topic: str | None = None) -> Self: ...

    @overload
    def add(self, type: OhItemTypeLiteral, name: str, value: Any = None, *,
            last_value: Any = None, label: str | None = None, tags: OhGroupType | None = None,
            groups: OhGroupType | None = None, metadata: MetadataDict | None = None) -> Self: ...

    def add(self, type: Any, name: str, value: Any = None, **kwargs: Any) -> Self:
        result: dict[str, Any] = {'type': type, 'name': name, 'value': value}
        result.update(kwargs)
        self._items.append(result)
        return self


# noinspection PyShadowingBuiltins
class TestingItemFactory:
    def __init__(self, event_bus: EventBus, oh_registry_handler: OhItemRegistryHandler,
                 if_oh: OpenHabSyncInterface, if_mqtt: MqttInterface) -> None:
        self._eb: Final = event_bus
        self._oh_registry_handler: Final = oh_registry_handler
        self._if_oh: Final = if_oh
        self._if_mqtt: Final = if_mqtt

    async def create_items(self, cfgs: list[dict[str, Any]]) -> None:
        for cfg in cfgs:
            await self.create(**cfg)
        cfgs.clear()
        return None

    @overload
    async def create(self, type: Literal['Item'] | type[Item], name: str, value: Any = None, *,
                     last_value: Any = None) -> Item: ...

    @overload
    async def create(self, type: Literal['MqttItem'] | type[MqttItem], name: str, value: Any = None, *,
                     last_value: Any = None) -> MqttItem: ...

    @overload
    async def create(self, type: Literal['MqttPairItem'] | type[MqttPairItem], name: str, value: Any = None, *,
                     last_value: Any = None, write_topic: str | None = None) -> MqttPairItem: ...

    async def create(self, type: str | type[BaseItem], name: str, value: Any = None, *,
                     last_value: Any = None, **kwargs: Any) -> BaseItem:
        if isinstance(type, str):
            classes = (
                Item, MqttItem, MqttPairItem,
                StringItem, NumberItem, SwitchItem, ContactItem, RollershutterItem, DimmerItem, DatetimeItem,
                ColorItem, ImageItem, GroupItem, PlayerItem, LocationItem, CallItem
            )

            d = {c.__name__: c for c in classes}
            for _name, _cls in tuple(d.items()):
                _name = _name.removesuffix('Item')
                if not _name:
                    continue
                assert _name not in d
                d[_name] = _cls

            type = d.get(type, type)

        if not isclass(type) or not issubclass(type, BaseItem):
            msg = f'Invalid type: {type}'
            raise TypeError(msg)

        kwargs['event_bus'] = self._eb

        if issubclass(type, MqttBaseItem):
            kwargs['interface'] = self._if_mqtt

        if issubclass(type, OpenhabItem):
            kwargs['interface'] = self._if_oh

        obj = type(name=name, initial_value=value, last_value=last_value, **kwargs)

        if isinstance(obj, OpenhabItem):
            self._oh_registry_handler.add_to_registry(obj)

        return obj
