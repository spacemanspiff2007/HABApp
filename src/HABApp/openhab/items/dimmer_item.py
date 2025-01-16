from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.openhab.definitions import (
    IncreaseDecreaseType,
    OnOffType,
    OnOffValue,
    PercentType,
    PercentValue,
    RefreshType,
    UnDefType,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh
from HABApp.openhab.items.commands import OnOffCommand, PercentCommand


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/DimmerItem.java
class DimmerItem(OpenhabItem, OnOffCommand, PercentCommand):
    """DimmerItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar int | float value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('DimmerItem', PercentType, OnOffType, UnDefType)
    _command_to_oh: Final = ValueToOh('DimmerItem', PercentType, OnOffType, IncreaseDecreaseType, RefreshType)
    _state_from_oh_str: Final = staticmethod(PercentType.from_oh_str)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = 100 if new_value.is_on else 0
        elif isinstance(new_value, PercentValue):
            new_value = new_value.value

        # Percent is 0 ... 100
        if isinstance(new_value, (int, float)) and (0 <= new_value <= 100):
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValueError.from_item(self, new_value)

    def is_on(self) -> bool:
        """Test value against on-value"""
        return bool(self.value)

    def is_off(self) -> bool:
        """Test value against off-value"""
        return self.value is not None and not self.value

    def __str__(self) -> str:
        return str(self.value)

    def __bool__(self) -> bool:
        if self.value is None:
            raise ItemValueIsNoneError.from_item(self)
        return self.is_on()
