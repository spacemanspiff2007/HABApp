from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from HABApp.openhab.definitions.websockets.item_value_types import RefreshTypeModel, StringTypeModel, UnDefTypeModel
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent


if TYPE_CHECKING:
    MetaData = MetaData     # noqa: PLW0127
    Mapping = Mapping       # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/StringItem.java
class StringItem(OpenhabItem):
    """StringItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    # Undef has to become before StringType
    _update_to_oh: Final = OutgoingStateEvent('StringItem', UnDefTypeModel, StringTypeModel)
    _command_to_oh: Final = OutgoingCommandEvent('StringItem', RefreshTypeModel, StringTypeModel)
    _state_from_oh_str: Final = staticmethod(StringTypeModel.get_value_from_state)
