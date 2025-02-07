from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.errors import InvalidItemValueError
from HABApp.core.types import Point
from HABApp.openhab.definitions.websockets.item_value_types import PointTypeModel
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/LocationItem.java
class LocationItem(OpenhabItem):
    """LocationItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Point value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('LocationItem', PointTypeModel, 'UnDef')
    _command_to_oh: Final = OutgoingCommandEvent('LocationItem', PointTypeModel, 'Refresh')
    _state_from_oh_str: Final = staticmethod(PointTypeModel.get_value_from_state)

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, Point):
            return super().set_value(new_value)

        if isinstance(new_value, tuple) and len(new_value) in (2, 3):
            return super().set_value(Point(*new_value))

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValueError.from_item(self, new_value)

