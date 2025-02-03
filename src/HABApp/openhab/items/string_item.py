from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.openhab.definitions import (
    RefreshType,
    StringType,
    UnDefType,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh


if TYPE_CHECKING:
    MetaData = MetaData     # noqa: PLW0127
    Mapping = Mapping       # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/StringItem.java
class StringItem(OpenhabItem):
    """StringItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    # Undef has to become before StringType
    _update_to_oh: Final = ValueToOh('StringItem', UnDefType, StringType)
    _command_to_oh: Final = ValueToOh('StringItem', StringType, RefreshType)
    _state_from_oh_str: Final = staticmethod(StringType.from_oh_str)
