from typing import Tuple, Union
from HABApp.core.items.base_item import BaseItem, TYPE_ITEM


class ItemRegistryBase:

    def item_exists(self, name: str) -> bool:
        raise NotImplementedError()

    def get_item(self, name: str) -> BaseItem:
        raise NotImplementedError()

    def get_item_names(self) -> Tuple[str, ...]:
        raise NotImplementedError()

    def add_item(self, item: TYPE_ITEM) -> TYPE_ITEM:
        raise NotImplementedError()

    def pop_item(self, name: Union[str, TYPE_ITEM]) -> TYPE_ITEM:
        raise NotImplementedError()
