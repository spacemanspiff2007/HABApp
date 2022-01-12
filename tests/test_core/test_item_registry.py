from HABApp.core import Items
from HABApp.core.items import Item


def test_basics():
    name = 'test'
    created_item = Item(name)
    Items.add_item(created_item)

    assert Items.item_exists(name)
    assert created_item is Items.get_item(name)

    assert Items.get_item_names() == (name, )
    assert Items.get_items() == (created_item, )

    assert created_item == Items.pop_item(name)
    assert Items.get_items() == tuple()
