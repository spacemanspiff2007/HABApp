from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final

from HABApp.core.events import ComplexEventValue
from HABApp.openhab.definitions import OpenHABDataType, UnDefType
from HABApp.openhab.item_to_reg import get_members
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, ValueToOh


if TYPE_CHECKING:
    Any = Any
    Mapping = Mapping
    MetaData = MetaData


class LetEverythingPassType(OpenHABDataType):

    @staticmethod
    def to_oh_str(value: Any) -> str | None:
        return value

    @staticmethod
    def from_oh_str(value: str) -> Any:
        return value


class GroupItem(OpenhabItem):
    """GroupItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Any value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = ValueToOh('GroupItem', UnDefType, LetEverythingPassType)
    _command_to_oh: Final = ValueToOh('GroupItem', LetEverythingPassType)
    _state_from_oh_str = staticmethod(LetEverythingPassType.from_oh_str)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, ComplexEventValue):
            new_value = new_value.value
        return super().set_value(new_value)

    @property
    def members(self) -> tuple[OpenhabItem, ...]:
        """Resolves and then returns all group members"""

        return get_members(self.name)
