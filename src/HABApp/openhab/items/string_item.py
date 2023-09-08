from typing import TYPE_CHECKING, Optional, FrozenSet, Mapping

from HABApp.openhab.items.base_item import OpenhabItem, MetaData

if TYPE_CHECKING:
    MetaData = MetaData
    Optional = Optional
    FrozenSet = FrozenSet,
    Mapping = Mapping


class StringItem(OpenhabItem):
    """StringItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar Optional[str] label: |oh_item_desc_label|
    :ivar FrozenSet[str] tags: |oh_item_desc_tags|
    :ivar FrozenSet[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        return state


class PlayerItem(OpenhabItem):
    """PlayerItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar str value: |oh_item_desc_value|

    :ivar Optional[str] label: |oh_item_desc_label|
    :ivar FrozenSet[str] tags: |oh_item_desc_tags|
    :ivar FrozenSet[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        return state
