from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions import (
    RefreshType,
    StringListType,
    UnDefType,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/CallItem.java
class CallItem(OpenhabItem):
    """CallItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar tuple[str, ...] value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('CallItem', StringListType, UnDefType)
    _command_to_oh: Final = ValueToOh('CallItem', RefreshType)
    _state_from_oh_str: Final = staticmethod(StringListType.from_oh_str)

    @override
    def set_value(self, new_value: str | tuple[str, ...] | None) -> bool:
        if isinstance(new_value, tuple):
            if not all(isinstance(x, str) for x in new_value):
                raise InvalidItemValueError.from_item(self, new_value)
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(None)

        if isinstance(new_value, str):
            return super().set_value(StringListType.from_oh_str(new_value))

        raise InvalidItemValueError.from_item(self, new_value)
