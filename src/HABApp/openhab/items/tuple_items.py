from collections.abc import Mapping
from typing import TYPE_CHECKING

from HABApp.openhab.definitions.values import PointValue
from HABApp.openhab.items.base_item import MetaData, OpenhabItem


if TYPE_CHECKING:
    Mapping = Mapping
    MetaData = MetaData


class CallItem(OpenhabItem):
    """CallItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar tuple[str, ...] value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        return tuple(state.split(','))

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, str):
            return super().set_value(tuple(new_value.split(',')))

        if isinstance(new_value, tuple):
            return super().set_value(new_value)

        assert new_value is None
        return super().set_value(tuple())


class LocationItem(OpenhabItem):
    """LocationItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar tuple[float, float, float | None] | None value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    @staticmethod
    def _state_from_oh_str(state: str):
        value = tuple(state.split(','))
        assert 2 <= len(value) <= 3
        return value

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, PointValue):
            return super().set_value(new_value.value)

        if new_value is None:
            return super().set_value(new_value)

        if isinstance(new_value, tuple):
            assert 2 <= len(new_value) <= 3
            return super().set_value(new_value)

        parts = new_value.split(',')    # type: list[Optional[str]]
        if len(parts) == 2:
            parts.append(None)
        assert len(parts) == 3
        return super().set_value(tuple(parts))
