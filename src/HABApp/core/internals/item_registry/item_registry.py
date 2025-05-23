from __future__ import annotations

import logging
import threading
from typing import Final, TypeVar, overload

from HABApp.core.errors import ItemAlreadyExistsError, ItemNotFoundException
from HABApp.core.internals.item_registry import ItemRegistryItem


ITEM_TYPE = TypeVar('ITEM_TYPE', bound=ItemRegistryItem)

log = logging.getLogger('HABApp.Items')


# noinspection PyProtectedMember
class ItemRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: Final[dict[str, ItemRegistryItem]] = {}

    def item_exists(self, name: str | ItemRegistryItem) -> bool:
        if not isinstance(name, str):
            name = name.name
        return name in self._items

    def get_item(self, name: str) -> ItemRegistryItem:
        try:
            return self._items[name]
        except KeyError:
            raise ItemNotFoundException(name) from None

    def get_items(self) -> tuple[ItemRegistryItem, ...]:
        return tuple(self._items.values())

    def get_item_names(self) -> tuple[str, ...]:
        return tuple(self._items.keys())

    def add_item(self, item: ITEM_TYPE) -> ITEM_TYPE:
        if not isinstance(item, ItemRegistryItem):
            msg = f'Item must be of type {ItemRegistryItem.__name__} not {type(item)}'
            raise TypeError(msg)

        name = item.name

        with self._lock:
            existing = self._items.get(name)
            if existing is not None:
                # adding the same item multiple times will not cause an exception
                if existing is item:
                    return item

                # adding a new item with the same name raises an exception
                raise ItemAlreadyExistsError(name)

            self._items[name] = item

        log.debug(f'Added {name} ({item.__class__.__name__})')
        item._on_item_added()
        return item

    @overload
    def pop_item(self, name: ITEM_TYPE) -> ITEM_TYPE:
        ...

    @overload
    def pop_item(self, name: str) -> ItemRegistryItem:
        ...

    def pop_item(self, name: str | ItemRegistryItem) -> ItemRegistryItem:
        if not isinstance(name, str):
            name = name.name

        with self._lock:
            try:
                item = self._items.pop(name)
            except KeyError:
                raise ItemNotFoundException(name) from None

        log.debug(f'Removed {name} ({item.__class__.__name__})')
        item._on_item_removed()
        return item

    def __bool__(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)
