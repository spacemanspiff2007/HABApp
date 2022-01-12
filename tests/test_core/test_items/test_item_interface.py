import pytest

from HABApp.core import Items
from HABApp.core.errors import ItemNotFoundException, ItemAlreadyExistsError
from HABApp.core.items import Item


def test_pop():
    Items.add_item(Item('test'))
    assert Items.item_exists('test')

    with pytest.raises(ItemNotFoundException):
        Items.pop_item('asdfadsf')

    Items.pop_item('test')
    assert not Items.item_exists('test')


def test_add():
    added = Item('test')
    Items.add_item(added)
    assert Items.item_exists('test')

    # adding the same item multiple times will not cause an exception
    Items.add_item(added)
    Items.add_item(added)

    # adding a new item -> exception
    with pytest.raises(ItemAlreadyExistsError):
        Items.add_item(Item('test'))
