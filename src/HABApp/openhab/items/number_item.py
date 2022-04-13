from typing import Optional, FrozenSet, Mapping

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from ..definitions import QuantityValue


class NumberItem(OpenhabItem):
    """NumberItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar Union[int, float] value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """


    @classmethod
    def from_oh(cls, name: str, value=None, label: Optional[str] = None, tags: FrozenSet[str] = frozenset(),
                groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):
        if value is None:
            return cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)

        try:
            value = int(value)
        except ValueError:
            value = float(value)
        return cls(name, value, label, tags, groups, metadata)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)
