import logging
import threading
from typing import Dict, Union, Tuple

from HABApp.core.errors import ItemNotFoundException, ItemAlreadyExistsError
from HABApp.core.base import ItemRegistryBase, BaseItem, TYPE_ITEM_OBJ

log = logging.getLogger('HABApp.Items')


class ItemRegistry(ItemRegistryBase):
    def __init__(self):
        self._lock = threading.Lock()
        self._items: Dict[str, TYPE_ITEM_OBJ] = {}

    def item_exists(self, name: Union[str, TYPE_ITEM_OBJ]) -> bool:
        if isinstance(name, BaseItem):
            name = name.name
        return name in self._items

    def get_item(self, name: str) -> TYPE_ITEM_OBJ:
        try:
            return self._items[name]
        except KeyError:
            raise ItemNotFoundException(name) from None

    def get_items(self) -> Tuple[TYPE_ITEM_OBJ, ...]:
        return tuple(self._items.values())

    def get_item_names(self) -> Tuple[str, ...]:
        return tuple(self._items.keys())

    def add_item(self, item: TYPE_ITEM_OBJ) -> TYPE_ITEM_OBJ:
        assert isinstance(item, BaseItem), type(item)
        name = item.name

        with self._lock:
            existing = self._items.get(name)
            if existing is not None:
                # adding the same item multiple times will not cause an exception
                if existing is item:
                    return TYPE_ITEM_OBJ

                # adding a new item with the same name raises an exception
                raise ItemAlreadyExistsError(name)

            self._items[name] = item

        log.debug(f'Added {name} ({item.__class__.__name__})')
        item._on_item_added()
        return item

    def pop_item(self, name: Union[str, TYPE_ITEM_OBJ]) -> TYPE_ITEM_OBJ:
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
