from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final, override

from immutables import Map

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.openhab.definitions.websockets.item_value_types import (
    DecimalTypeModel,
    QuantityTypeModel,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent


if TYPE_CHECKING:
    MetaData = MetaData     # noqa: PLW0127
    Mapping = Mapping       # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/NumberItem.java
class NumberItem(OpenhabItem):
    """NumberItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar int | float value: |oh_item_desc_value|
    :ivar str | None dimension: Dimension if it's a UoM item
    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('NumberItem', DecimalTypeModel, QuantityTypeModel, 'UnDef')
    _command_to_oh: Final = OutgoingCommandEvent('NumberItem', DecimalTypeModel, QuantityTypeModel, 'Refresh')

    def __init__(self, name: str, initial_value: int | float = None, label: str | None = None,
                 tags: frozenset[str] = frozenset(), groups: frozenset[str] = frozenset(),
                 metadata: Mapping[str, MetaData] = Map(), dimension: str | None = None) -> None:
        super().__init__(name, initial_value, label, tags, groups, metadata)
        self.dimension: str | None = dimension

    @override
    def _update_item_definition(self, item: 'NumberItem') -> None:
        super()._update_item_definition(item)
        self.dimension = item.dimension

    @staticmethod
    def _state_from_oh_str(state: str) -> int | float:
        if ' ' not in state:
            return DecimalTypeModel.get_value_from_state(state)
        return QuantityTypeModel.get_value_from_state(state)

    @property
    def unit(self) -> str | None:
        """Return the item unit if it is a "Unit of Measurement" item else None"""
        if (unit := self.metadata.get('unit')) is None:
            return None
        return unit.value

    def set_value(self, new_value: float | None) -> bool:

        if isinstance(new_value, (int, float)):
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValueError.from_item(self, new_value)

    def __bool__(self) -> bool:
        if self.value is None:
            raise ItemValueIsNoneError.from_item(self)
        return bool(self.value)
