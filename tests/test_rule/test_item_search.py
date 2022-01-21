import pytest

from HABApp import Rule
from HABApp.core import Items
from HABApp.core.base import BaseValueItem
from HABApp.core.items import Item
from HABApp.openhab.items import OpenhabItem, SwitchItem
from HABApp.openhab.items.base_item import MetaData


def test_search_type():
    item1 = BaseValueItem('item_1')
    item2 = Item('item_2')

    assert Rule.get_items() == []

    Items.add_item(item1)
    Items.add_item(item2)

    assert Rule.get_items() == [item1, item2]
    assert Rule.get_items(type=BaseValueItem) == [item1, item2]
    assert Rule.get_items(type=(BaseValueItem, Item)) == [item1, item2]

    assert Rule.get_items(type=Item) == [item2]


def test_search_oh():
    item1 = OpenhabItem('oh_item_1', tags=frozenset(['tag1', 'tag2', 'tag3']),
                        groups=frozenset(['grp1', 'grp2']), metadata={'meta1': MetaData('meta_v1')})
    item2 = SwitchItem('oh_item_2', tags=frozenset(['tag1', 'tag2', 'tag4']),
                       groups=frozenset(['grp2', 'grp3']), metadata={'meta2': MetaData('meta_v2', config={'a': 'b'})})
    item3 = Item('item_2')

    assert Rule.get_items() == []

    Items.add_item(item1)
    Items.add_item(item2)
    Items.add_item(item3)

    assert Rule.get_items() == [item1, item2, item3]
    assert Rule.get_items(tags='tag2') == [item1, item2]
    assert Rule.get_items(tags='tag4') == [item2]

    assert Rule.get_items(groups='grp1') == [item1]
    assert Rule.get_items(groups='grp2') == [item1, item2]

    assert Rule.get_items(groups='grp1', tags='tag1') == [item1]
    assert Rule.get_items(groups='grp2', tags='tag4') == [item2]

    assert Rule.get_items(metadata='meta1') == [item1]
    assert Rule.get_items(metadata='meta2') == [item2]
    assert Rule.get_items(metadata=r'meta\d') == [item1, item2]

    assert Rule.get_items(metadata_value='meta_v1') == [item1]
    assert Rule.get_items(metadata_value='meta_v2') == [item2]
    assert Rule.get_items(metadata_value=r'meta_v\d') == [item1, item2]
    assert Rule.get_items(groups='grp1', metadata_value=r'meta_v\d') == [item1]


def test_classcheck():
    with pytest.raises(ValueError):
        Rule.get_items(Item, tags='asdf')


def test_search_name():
    item1 = BaseValueItem('item_1a')
    item2 = Item('item_2a')

    assert Rule.get_items() == []

    Items.add_item(item1)
    Items.add_item(item2)

    assert Rule.get_items() == [item1, item2]
    assert Rule.get_items(name=r'\da') == [item1, item2]
