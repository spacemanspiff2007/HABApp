from __future__ import annotations

from typing import Any, Final, Self

from HABApp.core.errors import ItemNameNotOfTypeStrError, ItemNotFoundException, WrongItemTypeError
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import BaseValueItem
from HABApp.core.provider import HABAPP_PROVIDER


class Item(BaseValueItem):
    """Simple item, used to store values in HABApp"""

    @classmethod
    def get_create_item(cls, name: str, initial_value: Any = None, last_value: Any = None) -> Self:
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :param last_value: last value the item will have if it gets created
        :return: The item
        """
        if not isinstance(name, str):
            raise ItemNameNotOfTypeStrError.from_value(name)

        item_registry: Final = HABAPP_PROVIDER.get_existing(ItemRegistry)
        event_bus: Final = HABAPP_PROVIDER.get_existing(EventBus)

        try:
            item = item_registry. get_item(name)
        except ItemNotFoundException:
            item = cls(name, initial_value, last_value, event_bus=event_bus)
            item_registry.add_item(item)

        if not isinstance(item, cls):
            raise WrongItemTypeError.from_item(item, cls)
        return item
