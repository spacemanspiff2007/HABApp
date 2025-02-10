from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final

from HABApp.core.const import MISSING
from HABApp.openhab.connection.plugins import post_update, send_command, send_websocket_event
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import RefreshTypeModel, StringTypeModel, UnDefTypeModel
from HABApp.openhab.item_to_reg import get_members
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent


if TYPE_CHECKING:
    Any = Any               # noqa: PLW0127
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

    _update_to_oh: Final = OutgoingStateEvent('GroupItem')
    _command_to_oh: Final = OutgoingCommandEvent('GroupItem')
    _state_from_oh_str = staticmethod(StringTypeModel.get_value_from_state)

    @property
    def members(self) -> tuple[OpenhabItem, ...]:
        """Resolves and then returns all group members"""

        return get_members(self.name)

    def oh_post_update(self, value: Any = MISSING) -> None:
        """Post an update to the openHAB item

        :param value: (optional) value to be posted. If not specified the current item value will be used.
        """
        new_value = self.value if value is MISSING else value

        if (obj := UnDefTypeModel.from_value(new_value)) is not None:
            send_websocket_event(ItemStateSendEvent.create(name=self._name, payload=obj))
            return None

        post_update(self._name, new_value, transport='http')
        return None

    def oh_send_command(self, value: Any = MISSING) -> None:
        """Send a command to the openHAB item

        :param value: (optional) value to be sent. If not specified the current item value will be used.
        """
        new_value = self.value if value is MISSING else value

        if (obj := RefreshTypeModel.from_value(new_value)) is not None:
            send_websocket_event(ItemCommandSendEvent.create(name=self._name, payload=obj))
            return None

        send_command(self._name, new_value, transport='http')
        return None
