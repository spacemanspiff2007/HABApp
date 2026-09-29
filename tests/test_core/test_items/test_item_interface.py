from unittest.mock import Mock

import pytest

from HABApp.core.errors import ItemAlreadyExistsError, ItemNotFoundException
from HABApp.core.internals import EventBus, ItemRegistry
from HABApp.core.items import Item


def test_pop() -> None:
    ir = ItemRegistry()
    ir.add_item(Item('test', event_bus=Mock(EventBus)))
    assert ir.item_exists('test')

    with pytest.raises(ItemNotFoundException):
        ir.pop_item('asdfadsf')

    ir.pop_item('test')
    assert not ir.item_exists('test')


def test_add() -> None:
    ir = ItemRegistry()
    added = Item('test', event_bus=Mock(EventBus))
    ir.add_item(added)
    assert ir.item_exists('test')

    # adding the same item multiple times will not cause an exception
    ir.add_item(added)
    ir.add_item(added)

    # adding a new item -> exception
    with pytest.raises(ItemAlreadyExistsError):
        ir.add_item(Item('test', event_bus=Mock(EventBus)))
