from typing import Optional, FrozenSet, Mapping

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from HABApp.openhab.items.commands import OnOffCommand, PercentCommand
from ..definitions import OnOffValue, PercentValue


class DimmerItem(OpenhabItem, OnOffCommand, PercentCommand):
    """DimmerItem which accepts and converts the data types from OpenHAB

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
        if value is not None:
            value = float(value)
        return cls(name, value, label=label, tags=tags, groups=groups, metadata=metadata)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = 100 if new_value.on else 0
        elif isinstance(new_value, PercentValue):
            new_value = new_value.value

        # Percent is 0 ... 100
        if isinstance(new_value, (int, float)):
            assert 0 <= new_value <= 100, new_value
        else:
            assert new_value is None, new_value

        return super().set_value(new_value)

    def __str__(self):
        return self.value

    def is_on(self) -> bool:
        """Test value against on-value"""
        return bool(self.value)

    def is_off(self) -> bool:
        """Test value against off-value"""
        return not bool(self.value)
