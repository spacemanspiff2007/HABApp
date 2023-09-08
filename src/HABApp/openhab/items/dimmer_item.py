from typing import Union, TYPE_CHECKING, Optional, FrozenSet, Mapping

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from HABApp.openhab.items.commands import OnOffCommand, PercentCommand
from ..definitions import OnOffValue, PercentValue

if TYPE_CHECKING:
    Union = Union
    Optional = Optional
    FrozenSet = FrozenSet
    Mapping = Mapping
    MetaData = MetaData


class DimmerItem(OpenhabItem, OnOffCommand, PercentCommand):
    """DimmerItem which accepts and converts the data types from OpenHAB

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
