from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions import (
    PointType,
    RefreshType,
    UnDefType,
)
from HABApp.openhab.definitions.values import PointValue
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/LocationItem.java
class LocationItem(OpenhabItem):
    """LocationItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar tuple[float, float, float | None] value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('LocationItem', PointType, UnDefType)
    _command_to_oh: Final = ValueToOh('LocationItem', PointType, RefreshType)
    _state_from_oh_str: Final = staticmethod(PointType.from_oh_str)

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, PointValue):
            return super().set_value(new_value.value)

        if isinstance(new_value, tuple):
            match len(new_value):
                case 3:
                    a, b, c = new_value
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and (
                            isinstance(c, (int, float)) or c is None):
                        return super().set_value(new_value)

                    raise InvalidItemValueError.from_item(self, new_value)

                case 2:
                    a, b = new_value
                    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                        return super().set_value((*new_value, None))

                    raise InvalidItemValueError.from_item(self, new_value)

            raise InvalidItemValueError.from_item(self, new_value)

        if new_value is None:
            return super().set_value(new_value)

        if isinstance(new_value, str):
            return super().set_value(PointType.from_oh_str(new_value))

        raise InvalidItemValueError.from_item(self, new_value)
