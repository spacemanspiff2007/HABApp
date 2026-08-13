from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Final

from immutables import Map

from HABApp.core.const import MISSING
from HABApp.core.internals import EventBus
from HABApp.openhab.connection.handler import OpenHabSyncInterface
from HABApp.openhab.definitions.helper import get_source
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent, ItemStateSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import RefreshTypeModel, StringTypeModel, UnDefTypeModel
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
from HABApp.openhab.items._event_builder import OutgoingCommandEvent, OutgoingStateEvent
from HABApp.openhab.items.base_item import MetaData, OpenhabItem


if TYPE_CHECKING:
    Any = Any               # noqa: PLW0127
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/GroupItem.java
class GroupItem(OpenhabItem):
    """GroupItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Any value: |oh_item_desc_value|
    :ivar Any last_value: |oh_item_desc_last_value|
    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('GroupItem')
    _command_to_oh: Final = OutgoingCommandEvent('GroupItem')
    _state_from_oh_str = staticmethod(StringTypeModel.get_value_from_state)

    def __init__(self, name: str, initial_value: Any = None, last_value: Any = None, label: str | None = None,
                 tags: frozenset[str] = frozenset(), groups: frozenset[str] = frozenset(),
                 metadata: Mapping[str, MetaData] = Map(), *,
                 event_bus: EventBus, interface: OpenHabSyncInterface, registry_handler: OhItemRegistryHandler) -> None:
        super().__init__(name, initial_value, last_value, label, tags, groups, metadata,
                         event_bus=event_bus, interface=interface)
        self._oh_registry_handler: Final = registry_handler

    @property
    def members(self) -> tuple[OpenhabItem, ...]:
        """Resolves and then returns all group members"""

        return self._oh_registry_handler.get_group_members(self.name)

    def oh_post_update(self, value: Any = MISSING, source: str | None = None) -> None:
        """Post an update to the openHAB item

        :param value: (optional) value to be posted. If not specified the current item value will be used.
        :param source: (optional) source where this update comes from
        """
        new_value = self.value if value is MISSING else value

        if (obj := UnDefTypeModel.from_value(new_value)) is not None:
            self._oh._send_websocket_event(
                ItemStateSendEvent.create(name=self._name, payload=obj, source=get_source(source))
            )
            return None

        self._oh.post_update(self._name, new_value, source=get_source(source), transport='http')
        return None

    def oh_send_command(self, value: Any = MISSING, *, source: str | None = None) -> None:
        """Send a command to the openHAB item

        :param value: (optional) value to be sent. If not specified the current item value will be used.
        :param source: (optional) source where this command comes from
        """
        new_value = self.value if value is MISSING else value

        if (obj := RefreshTypeModel.from_value(new_value)) is not None:
            self._oh._send_websocket_event(
                ItemCommandSendEvent.create(name=self._name, payload=obj, source=get_source(source))
            )
            return None

        self._oh.send_command(self._name, new_value, transport='http', source=get_source(source))
        return None
