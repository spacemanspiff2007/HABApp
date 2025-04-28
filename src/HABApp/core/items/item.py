from HABApp.core.errors import ItemNameNotOfTypeStrError, ItemNotFoundException, WrongItemTypeError
from HABApp.core.internals import uses_get_item, uses_item_registry
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
        if not isinstance(name, str):
            raise ItemNameNotOfTypeStrError.from_value(name)

        try:
            item = get_item(name)
        except ItemNotFoundException:
            item = cls(name, initial_value)
            item_registry.add_item(item)

        if not isinstance(item, cls):
            raise WrongItemTypeError.from_item(item, cls)
        return item
