from collections.abc import Mapping
from typing import TYPE_CHECKING

from fastnumbers import real

from HABApp.core.errors import InvalidItemValue, ItemValueIsNoneError
from HABApp.openhab.definitions import QuantityValue
from HABApp.openhab.items.base_item import MetaData, OpenhabItem


if TYPE_CHECKING:
    MetaData = MetaData
    Mapping = Mapping


class NumberItem(OpenhabItem):
    """NumberItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar int | float value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @property
    def unit(self) -> str | None:
        """Return the item unit if it is a "Unit of Measurement" item else None"""
        if (unit := self.metadata.get('unit')) is None:
            return None
        return unit.value

    @staticmethod
    def _state_from_oh_str(state: str):
        return real(state)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        if isinstance(new_value, (int, float)):
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValue.from_item(self, new_value)

    def __bool__(self):
        if self.value is None:
            raise ItemValueIsNoneError.from_item(self)
        return bool(self.value)
