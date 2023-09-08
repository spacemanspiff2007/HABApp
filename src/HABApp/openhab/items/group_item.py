from typing import TYPE_CHECKING, Optional, FrozenSet, Mapping, Tuple, Any

from HABApp.core.events import ComplexEventValue
from HABApp.openhab.item_to_reg import get_members
from HABApp.openhab.items.base_item import OpenhabItem, MetaData

if TYPE_CHECKING:
    Any = Any
    Optional = Optional
    FrozenSet = FrozenSet
    Mapping = Mapping
    MetaData = MetaData


class GroupItem(OpenhabItem):
    """GroupItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Any value: |oh_item_desc_value|

    :ivar Optional[str] label: |oh_item_desc_label|
    :ivar FrozenSet[str] tags: |oh_item_desc_tags|
    :ivar FrozenSet[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        return state

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, ComplexEventValue):
            new_value = new_value.value
        return super().set_value(new_value)

    @property
    def members(self) -> Tuple[OpenhabItem, ...]:
        """Resolves and then returns all group members"""

        return get_members(self.name)
