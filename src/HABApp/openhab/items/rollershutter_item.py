from collections.abc import Mapping
from typing import TYPE_CHECKING

from fastnumbers import real

from HABApp.core.errors import InvalidItemValue
from HABApp.openhab.definitions import PercentValue, UpDownValue
from HABApp.openhab.items.base_item import MetaData, OpenhabItem
from HABApp.openhab.items.commands import PercentCommand, UpDownCommand


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


class RollershutterItem(OpenhabItem, UpDownCommand, PercentCommand):
    """RollershutterItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar int | float value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        return real(state)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, UpDownValue):
            new_value = 0 if new_value.up else 100
        elif isinstance(new_value, PercentValue):
            new_value = new_value.value

        # Position is 0 ... 100
        if isinstance(new_value, (int, float)) and (0 <= new_value <= 100):
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValue.from_item(self, new_value)

    def is_up(self) -> bool:
        return self.value <= 0

    def is_down(self) -> bool:
        return self.value >= 100

    def __str__(self) -> str:
        return str(self.value)
