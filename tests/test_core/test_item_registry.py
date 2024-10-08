import pytest

from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import ItemRegistry
from HABApp.core.items import Item


def test_basics() -> None:
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


def test_errors() -> None:
    ir = ItemRegistry()

    with pytest.raises(TypeError, match="Name must be a string not <class 'int'>"):
        Item(name=123)

    with pytest.raises(TypeError, match="Item must be of type ItemRegistryItem not <class 'str'>"):
        ir.add_item('test')

    with pytest.raises(ItemNotFoundException, match='Item asdf does not exist!'):
        ir.get_item('asdf')
