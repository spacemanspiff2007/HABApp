from collections.abc import Mapping
from datetime import datetime
from typing import TYPE_CHECKING, Final

from HABApp.openhab.definitions import DateTimeType, RefreshType, UnDefType
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh


if TYPE_CHECKING:
    datetime = datetime
    Mapping = Mapping
    MetaData = MetaData


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/DateTimeItem.java
class DatetimeItem(OpenhabItem):
    """DateTimeItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar datetime value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('DatetimeItem', DateTimeType, UnDefType)
    _command_to_oh: Final = ValueToOh('DatetimeItem', DateTimeType, RefreshType)
    _state_from_oh_str: Final = staticmethod(DateTimeType.from_oh_str)
