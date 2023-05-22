from typing import FrozenSet, Mapping, Optional, Tuple, TYPE_CHECKING

from immutables import Map

from HABApp.openhab.definitions.values import PointValue
from HABApp.openhab.items.base_item import OpenhabItem, MetaData

if TYPE_CHECKING:
    Tuple = Tuple


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
            return super().set_value(tuple(new_value.split(',')))

        if isinstance(new_value, tuple):
            return super().set_value(new_value)

        assert new_value is None
        return super().set_value(tuple())


class LocationItem(OpenhabItem):
    """LocationItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar Optional[Tuple[float, float, Optional[float]]] value:

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
            assert 2 <= len(value) <= 3
        return cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, PointValue):
            return super().set_value(new_value.value)

        if new_value is None:
            return super().set_value(new_value)

        if isinstance(new_value, tuple):
            assert 2 <= len(new_value) <= 3
            return super().set_value(new_value)

        parts = new_value.split(',')    # type: list[Optional[str]]
        if len(parts) == 2:
            parts.append(None)
        assert len(parts) == 3
        return super().set_value(tuple(parts))
