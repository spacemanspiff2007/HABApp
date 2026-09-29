from unittest.mock import Mock

import pytest

from HABApp.core.errors import ItemNameNotOfTypeStrError, ItemNotFoundException
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import Item


def test_basics() -> None:
    item_name = 'test'

    ir = ItemRegistry()
    created_item = Item(item_name, event_bus=Mock(EventBus))
    ir.add_item(created_item)

    assert ir.item_exists(item_name)
    assert created_item is ir.get_item(item_name)

    assert ir.get_item_names() == (item_name, )
    assert ir.get_items() == (created_item, )

    assert created_item == ir.pop_item(item_name)
    assert ir.get_items() == ()


def test_errors() -> None:
    ir = ItemRegistry()

    with pytest.raises(ItemNameNotOfTypeStrError):
        Item(name=123, event_bus=Mock(EventBus))

    with pytest.raises(TypeError, match="Item must be of type ItemRegistryItem not <class 'str'>"):
        ir.add_item('test')

    with pytest.raises(ItemNotFoundException, match='Item asdf does not exist!'):
        ir.get_item('asdf')
