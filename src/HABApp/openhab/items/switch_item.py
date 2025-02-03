from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.openhab.definitions import (
    OnOffType,
    OnOffValue,
    RefreshType,
    UnDefType,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh
from HABApp.openhab.items.commands import OnOffCommand


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


ON: Final = OnOffType.ON
OFF: Final = OnOffType.OFF


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/SwitchItem.java
class SwitchItem(OpenhabItem, OnOffCommand):
    """SwitchItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('SwitchItem', OnOffType, UnDefType)
    _command_to_oh: Final = ValueToOh('SwitchItem', OnOffType, RefreshType)
    _state_from_oh_str: Final = staticmethod(OnOffType.from_oh_str)

    def set_value(self, new_value: str | None) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = new_value.value

        if new_value not in (ON, OFF, None):
            raise InvalidItemValueError.from_item(self, new_value)

        return super().set_value(new_value)

    def is_on(self) -> bool:
        """Test value against on-value"""
        return self.value == ON

    def is_off(self) -> bool:
        """Test value against off-value"""
        return self.value == OFF

    def toggle(self):
        """Toggle the switch. Turns the switch on when off or off when currently on."""
        if self.value == ON:
            self.off()
        elif self.value == OFF:
            self.on()
        elif self.value is None:
            raise ItemValueIsNoneError.from_item(self)
        else:
            raise InvalidItemValueError.from_item(self, self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SwitchItem):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, int):
            if other and self.is_on():
                return True
            if not other and self.is_off():
                return True
            return False

        return NotImplemented

    def __bool__(self) -> bool:
        if self.value is None:
            raise ItemValueIsNoneError.from_item(self)
        return self.value == ON
