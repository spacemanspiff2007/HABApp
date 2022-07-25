from typing import Tuple

from HABApp.core.events import ComplexEventValue
from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.item_to_reg import get_members


class GroupItem(OpenhabItem):
    """GroupItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar str value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, ComplexEventValue):
            new_value = new_value.value
        return super().set_value(new_value)

    @property
    def members(self) -> Tuple[OpenhabItem, ...]:
        """Resolves and then returns all group members"""

        return get_members(self.name)
