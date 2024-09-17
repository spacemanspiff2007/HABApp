from HABApp.core.items import Item

from . import ItemTests


class TestItem(ItemTests):
    ITEM_CLASS = Item
    ITEM_VALUES = (0, 'str', (1, 2, 3))
