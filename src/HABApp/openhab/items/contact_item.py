from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from HABApp.openhab.interface_sync import post_update
from HABApp.openhab.items.base_item import MetaData, OpenhabItem

from ...core.const import MISSING
from ...core.errors import InvalidItemValue
from ..definitions import OpenClosedValue
from ..errors import SendCommandNotSupported


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


OPEN = OpenClosedValue.OPEN
CLOSED = OpenClosedValue.CLOSED


class ContactItem(OpenhabItem):
    """ContactItem

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        if state != OPEN and state != CLOSED:
            raise ValueError(f'Invalid value for ContactItem: {state}')
        return state

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OpenClosedValue):
            new_value = new_value.value

        if new_value not in (OPEN, CLOSED, None):
            raise InvalidItemValue.from_item(self, new_value)

        return super().set_value(new_value)

    def is_open(self) -> bool:
        """Test value against open value"""
        return self.value == OPEN

    def is_closed(self) -> bool:
        """Test value against closed value"""
        return self.value == CLOSED

    def oh_send_command(self, value: Any = MISSING):
        msg = f'{self.__class__.__name__} does not support send command! See openHAB documentation for details.'
        raise SendCommandNotSupported(msg)

    def open(self):
        """Post an update to the item with the open value"""
        return post_update(self.name, OPEN)

    def closed(self):
        """Post an update to the item with the closed value"""
        return post_update(self.name, CLOSED)

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
