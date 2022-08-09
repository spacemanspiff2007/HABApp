from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import uses_item_registry, uses_get_item
from HABApp.core.items import BaseValueItem

get_item = uses_get_item()
item_registry = uses_item_registry()


class Item(BaseValueItem):
    """Simple item, used to store values in HABApp"""

    @classmethod
    def get_create_item(cls, name: str, initial_value=None) -> 'Item':
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :return: The item
        """
        assert isinstance(name, str), type(name)

        try:
            item = get_item(name)
        except ItemNotFoundException:
            item = cls(name, initial_value)
            item_registry.add_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item
