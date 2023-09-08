from typing import TYPE_CHECKING, Optional, FrozenSet, Mapping, Union

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from HABApp.openhab.items.commands import UpDownCommand, PercentCommand
from ..definitions import UpDownValue, PercentValue

if TYPE_CHECKING:
    Union = Union
    Optional = Optional
    FrozenSet = FrozenSet
    Mapping = Mapping
    MetaData = MetaData


class RollershutterItem(OpenhabItem, UpDownCommand, PercentCommand):
    """RollershutterItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Union[int, float] value: |oh_item_desc_value|

    :ivar Optional[str] label: |oh_item_desc_label|
    :ivar FrozenSet[str] tags: |oh_item_desc_tags|
    :ivar FrozenSet[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        try:
            return int(state)
        except ValueError:
            return float(state)

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
