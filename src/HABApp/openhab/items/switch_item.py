from typing import TYPE_CHECKING, Tuple, Optional, FrozenSet, Mapping

from HABApp.openhab.definitions import OnOffValue
from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from HABApp.openhab.items.commands import OnOffCommand

if TYPE_CHECKING:
    Tuple = Tuple
    Optional = Optional
    FrozenSet = FrozenSet
    Mapping = Mapping
    MetaData = MetaData


ON = OnOffValue.ON
OFF = OnOffValue.OFF


class SwitchItem(OpenhabItem, OnOffCommand):
    """SwitchItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar Optional[str] label: |oh_item_desc_label|
    :ivar FrozenSet[str] tags: |oh_item_desc_tags|
    :ivar FrozenSet[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """


    @staticmethod
    def _state_from_oh_str(state: str):
        if state != ON and state != OFF:
            raise ValueError(f'Invalid value for SwitchItem: {state}')
        return state

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = new_value.value

        if new_value is not None and new_value != ON and new_value != OFF:
            raise ValueError(f'Invalid value for SwitchItem {self.name}: {new_value}')
        return super().set_value(new_value)

    def is_on(self) -> bool:
        """Test value against on-value"""
        return self.value == ON

    def is_off(self) -> bool:
        """Test value against off-value"""
        return self.value == OFF

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, SwitchItem):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        elif isinstance(other, int):
            if other and self.is_on():
                return True
            if not other and self.is_off():
                return True
            return False

        return NotImplemented

    def __bool__(self):
        return self.is_on()
