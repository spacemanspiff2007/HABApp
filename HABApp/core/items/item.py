import HABApp
from . import BaseValueItem


class Item(BaseValueItem):
    """Simple item, used to store values in HABApp

    :ivar str ~.name: Name of the item (read only)
    :ivar ~.value: Value of the item, can be anything (read only)
    :ivar ~.datetime.datetime last_change: Timestamp of the last time when the item has changed the value (read only)
    :ivar ~.datetime.datetime last_update: Timestamp of the last time when the item has updated the value (read only)
    """

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
            HABApp.core.Items.set_item(item)

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item
