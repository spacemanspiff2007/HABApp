from typing import Optional, FrozenSet, Mapping

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from HABApp.openhab.items.commands import UpDownCommand, PercentCommand
from ..definitions import UpDownValue, PercentValue


class RollershutterItem(OpenhabItem, UpDownCommand, PercentCommand):
    """RollershutterItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar Union[int, float] value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    def __init__(self, name: str, initial_value=None, label: Optional[str] = None, tags: FrozenSet[str] = frozenset(),
                 groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):
        if initial_value is not None:
            initial_value = float(initial_value)
        super().__init__(name, initial_value, label, tags, groups, metadata)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, UpDownValue):
            new_value = 0 if new_value.up else 100
        elif isinstance(new_value, PercentValue):
            new_value = new_value.value

        assert isinstance(new_value, (int, float)) or new_value is None, new_value
        return super().set_value(new_value)

    def is_up(self) -> bool:
        return self.value <= 0

    def is_down(self) -> bool:
        return self.value >= 100

    def __str__(self):
        return self.value
