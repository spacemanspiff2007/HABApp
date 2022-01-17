from typing import FrozenSet, Mapping

from immutables import Map

from HABApp.openhab.items.base_item import OpenhabItem, MetaData


class CallItem(OpenhabItem):
    """CallItem which accepts and converts the data types from OpenHAB"""

    def __init__(self, name: str, initial_value=None, tags: FrozenSet[str] = frozenset(),
                 groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):

        if isinstance(initial_value, str):
            initial_value = tuple(initial_value.split(','))
        super().__init__(name, initial_value, tags, groups, metadata)

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, str):
            new_value = tuple(new_value.split(','))
        return super().set_value(new_value)
