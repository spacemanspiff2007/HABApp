import inspect

import pytest

from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.map_items import _items as item_dict
from HABApp.openhab.items import Thing


@pytest.mark.parametrize('cls', (c for c in item_dict.values()))
def test_argspec_from_oh(cls):
    target_spec = inspect.getfullargspec(OpenhabItem.from_oh)
    current_spec = inspect.getfullargspec(cls.from_oh)
    assert current_spec == target_spec


@pytest.mark.parametrize('cls', tuple(c for c in item_dict.values()) + (Thing, ))
def test_set_name(cls):

    # test that we can set the name properly
    c = cls('asdf')
    assert c.name == 'asdf'

    # this test ensures that all openHAB items inherit from OpenhabItem
    if cls is not Thing:
        assert isinstance(c, OpenhabItem)
