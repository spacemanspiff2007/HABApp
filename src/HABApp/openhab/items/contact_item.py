from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions.websockets.item_value_types import OpenClosedTypeModel
from HABApp.openhab.interface_sync import post_update
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/ContactItem.java
class ContactItem(OpenhabItem):
    """ContactItem

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('ContactItem', 'OpenClosed', 'UnDef')
    _command_to_oh: Final = OutgoingCommandEvent('ContactItem', 'Refresh')
    _state_from_oh_str = staticmethod(OpenClosedTypeModel.get_value_from_state)

    def set_value(self, new_value) -> bool:

        if new_value not in ('OPEN', 'CLOSED', None):
            raise InvalidItemValueError.from_item(self, new_value)

        return super().set_value(new_value)

    def is_open(self) -> bool:
        """Test value against open value"""
        return self.value == 'OPEN'

    def is_closed(self) -> bool:
        """Test value against closed value"""
        return self.value == 'CLOSED'

    def open(self) -> None:
        """Post an update to the item with the open value"""
        return post_update(self.name, 'OPEN')

    def closed(self) -> None:
        """Post an update to the item with the closed value"""
        return post_update(self.name, 'CLOSED')

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, ContactItem):
            return self.value == other.value

        if isinstance(other, str):
            return self.value == other

        if isinstance(other, int):
            if other and self.is_open():
                return True
            if not other and self.is_closed():
                return True
            return False

        return NotImplemented
