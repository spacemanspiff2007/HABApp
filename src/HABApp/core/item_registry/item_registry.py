import logging
import threading
from typing import Dict, Union, Tuple

from HABApp.core.errors import ItemNotFoundException, ItemAlreadyExistsError
from HABApp.core.item_registry import ItemRegistryBase
from HABApp.core.items.base_item import BaseItem, TYPE_ITEM

log = logging.getLogger('HABApp.Items')


class ItemRegistry(ItemRegistryBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._items: Dict[str, TYPE_ITEM] = {}

    def item_exists(self, name: Union[str, TYPE_ITEM]) -> bool:
        if isinstance(name, BaseItem):
            name = name.name
        return name in self._items

    def get_item(self, name: str) -> TYPE_ITEM:
        try:
            return self._items[name]
        except KeyError:
            raise ItemNotFoundException(name) from None

    def get_items(self) -> Tuple[TYPE_ITEM, ...]:
        return tuple(self._items.values())

    def get_item_names(self) -> Tuple[str, ...]:
        return tuple(self._items.keys())

    def add_item(self, item: TYPE_ITEM) -> TYPE_ITEM:
        assert isinstance(item, BaseItem), type(item)
        name = item.name

        with self._lock:
            existing = self._items.get(name)
            if existing is not None:
                # adding the same item multiple times will not cause an exception
                if existing is item:
                    return TYPE_ITEM

                # adding a new item with the same name raises an exception
                raise ItemAlreadyExistsError(name)

            self._items[name] = item

        log.debug(f'Added {name} ({item.__class__.__name__})')
        item._on_item_added()
        return item

    def pop_item(self, name: Union[str, TYPE_ITEM]) -> TYPE_ITEM:
        if isinstance(name, BaseItem):
            name = name.name

        with self._lock:
            try:
                item = self._items.pop(name)
            except KeyError:
                raise ItemNotFoundException(name) from None

        log.debug(f'Removed {name} ({item.__class__.__name__})')
        item._on_item_removed()
        return item
