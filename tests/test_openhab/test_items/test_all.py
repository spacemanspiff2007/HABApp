import inspect

import pytest

from HABApp.openhab.items import Thing, ColorItem, ImageItem
from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.map_items import _items as item_dict
from tests.helpers.docs import get_ivars


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


@pytest.mark.parametrize('cls', (c for c in item_dict.values()))
def test_doc_ivar(cls):

    class_vars = get_ivars(cls)

    # test that the class has the corresponding attribute
    obj = cls(name='test')
    for name in class_vars:
        assert hasattr(obj, name)

    if cls is ColorItem:
        class_vars.pop('hue')
        class_vars.pop('saturation')
        class_vars.pop('brightness')

    if cls is ImageItem:
        class_vars.pop('image_type')

    class_vars.pop('value')

    # compare with base class so we have a consistent signature
    target_vars = get_ivars(OpenhabItem)
    target_vars.pop('value')
    assert target_vars == class_vars

