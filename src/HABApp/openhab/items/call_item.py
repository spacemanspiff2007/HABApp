from typing import FrozenSet, Mapping, Optional

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData


class CallItem(OpenhabItem):
    """CallItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar Tuple[str, ...] value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    @classmethod
    def from_oh(cls, name: str, value=None, label: Optional[str] = None, tags: FrozenSet[str] = frozenset(),
                groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):
        if value is not None:
            value = tuple(value.split(','))
        return cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, str):
            new_value = tuple(new_value.split(','))
        return super().set_value(new_value)
