from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from HABApp.core.const import MISSING
from HABApp.core.const.const import _MissingType
from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions.websockets.item_value_types import StringListTypeModel
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent
from HABApp.openhab.types import StringList


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/CallItem.java
class CallItem(OpenhabItem):
    """CallItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar StringList value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('CallItem', 'StringList', 'UnDef')
    _command_to_oh: Final = OutgoingCommandEvent('CallItem', 'Refresh')
    _state_from_oh_str: Final = staticmethod(StringListTypeModel.get_value_from_state)

    @override
    def set_value(self, new_value: tuple[str, ...] | list[str] | StringList | None) -> bool:
        if isinstance(new_value, StringList):
            return super().set_value(new_value)

        if new_value is None:
            return super().set_value(None)

        if isinstance(new_value, (tuple, list)):
            return super().set_value(StringList(new_value))

        raise InvalidItemValueError.from_item(self, new_value)

    @override
    def oh_post_update(self,
                       value: tuple[str, ...] | list[str] | StringList | None | _MissingType = MISSING) -> None:

        if isinstance(value, (tuple, list)):
            return super().oh_post_update(StringList(value))

        return super().oh_post_update(value)
