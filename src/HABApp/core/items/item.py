import HABApp
from . import BaseValueItem


class Item(BaseValueItem):
    """Simple item, used to store values in HABApp"""

    @classmethod
    def get_create_item(cls, name: str, initial_value=None):
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :return: item
        """
        assert isinstance(name, str), type(name)

        try:
            item = HABApp.core.Items.get_item(name)
        except HABApp.core.Items.ItemNotFoundException:
            item = cls(name, initial_value)
            HABApp.core.Items.add_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item
