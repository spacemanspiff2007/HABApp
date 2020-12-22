import pytest

from HABApp.core import Items
from HABApp.core.items import Item


@pytest.fixture
def clean_reg():
    Items._ALL_ITEMS.clear()
    yield
    Items._ALL_ITEMS.clear()


def test_pop(clean_reg):
    Items.add_item(Item('test'))
    assert Items.item_exists('test')

    with pytest.raises(Items.ItemNotFoundException):
        Items.pop_item('asdfadsf')

    Items.pop_item('test')
    assert not Items.item_exists('test')


def test_add(clean_reg):
    added = Item('test')
    Items.add_item(added)
    assert Items.item_exists('test')

    # adding the same item multiple times will not cause an exception
    Items.add_item(added)
    Items.add_item(added)

    # adding a new item -> exception
    with pytest.raises(Items.ItemAlreadyExistsError):
        Items.add_item(Item('test'))
