from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.openhab.definitions.websockets.item_value_types import StringTypeModel, UnDefTypeModel
from HABApp.openhab.item_to_reg import get_members
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/GroupItem.java
class GroupItem(OpenhabItem):
    """GroupItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Any value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('GroupItem', 'UnDef', 'String')
    _command_to_oh: Final = OutgoingCommandEvent('GroupItem', 'Refresh', 'String')
    _state_from_oh_str = staticmethod(StringTypeModel.get_value_from_state)

    def set_value(self, new_value) -> bool:
        return super().set_value(new_value)

    @property
    def members(self) -> tuple[OpenhabItem, ...]:
        """Resolves and then returns all group members"""

        return get_members(self.name)
