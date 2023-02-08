from HABApp.core.items import Item
from HABApp.core.internals import ItemRegistry


def test_basics():
    item_name = 'test'

    ir = ItemRegistry()
    created_item = Item(item_name)
    ir.add_item(created_item)

    assert ir.item_exists(item_name)
    assert created_item is ir.get_item(item_name)

    assert ir.get_item_names() == (item_name, )
    assert ir.get_items() == (created_item, )

    assert created_item == ir.pop_item(item_name)
    assert ir.get_items() == ()
