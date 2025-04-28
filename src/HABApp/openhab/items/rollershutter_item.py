from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions.websockets.item_value_types import (
    PercentTypeModel,
    RefreshTypeModel,
    StopMoveTypeModel,
    UnDefTypeModel,
    UpDownTypeModel,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent
from HABApp.openhab.items.commands import PercentCommand, UpDownCommand


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/RollershutterItem.java
class RollershutterItem(OpenhabItem, UpDownCommand, PercentCommand):
    """RollershutterItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar int | float value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('RollershutterItem', PercentTypeModel, UpDownTypeModel, UnDefTypeModel)
    _command_to_oh: Final = OutgoingCommandEvent(
        'RollershutterItem', UpDownTypeModel, StopMoveTypeModel, PercentTypeModel, RefreshTypeModel)
    _state_from_oh_str: Final = staticmethod(PercentTypeModel.get_value_from_state)

    def set_value(self, new_value) -> bool:

        # Position is 0 ... 100
        if isinstance(new_value, (int, float)) and (0 <= new_value <= 100):
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(new_value)

        raise InvalidItemValueError.from_item(self, new_value)

    def is_up(self) -> bool:
        return self.value <= 0

    def is_down(self) -> bool:
        return self.value >= 100

    def __str__(self) -> str:
        return str(self.value)
