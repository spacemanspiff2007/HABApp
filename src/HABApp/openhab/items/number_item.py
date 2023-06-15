from typing import Optional, FrozenSet, Mapping, Union, TYPE_CHECKING

from HABApp.openhab.items.base_item import OpenhabItem, MetaData
from ..definitions import QuantityValue

if TYPE_CHECKING:
    Union = Union
    MetaData = MetaData
    FrozenSet = FrozenSet
    Mapping = Mapping


class NumberItem(OpenhabItem):
    """NumberItem which accepts and converts the data types from OpenHAB

    :ivar str name:
    :ivar Union[int, float] value:

    :ivar Optional[str] label:
    :ivar FrozenSet[str] tags:
    :ivar FrozenSet[str] groups:
    :ivar Mapping[str, MetaData] metadata:
    """

    @property
    def unit(self) -> Optional[str]:
        """Return the item unit if it is a "Unit of Measurement" item else None"""
        if (unit := self.metadata.get('unit')) is None:
            return None
        return unit.value

    @staticmethod
    def _state_from_oh_str(state: str):
        try:
            return int(state)
        except ValueError:
            return float(state)

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)
