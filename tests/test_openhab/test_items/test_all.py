import inspect
from datetime import datetime
from typing import Any, Optional, Tuple, Union

import pytest

from HABApp.core.items import Item
from HABApp.openhab.items import (
    CallItem,
    ColorItem,
    ContactItem,
    DatetimeItem,
    DimmerItem,
    GroupItem,
    ImageItem,
    LocationItem,
    NumberItem,
    PlayerItem,
    RollershutterItem,
    StringItem,
    SwitchItem,
    Thing,
)
from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.map_items import _items as item_dict

from ...helpers.inspect import assert_same_signature, check_class_annotations, get_ivars_from_docstring


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
def test_conditional_function_call_signature(cls):
    assert_same_signature(Item.post_value_if, cls.post_value_if)
    assert_same_signature(Item.post_value_if, cls.oh_post_update_if)


@pytest.mark.parametrize('cls', (c for c in item_dict.values()))
def test_doc_ivar(cls):

    correct_hints = {
        StringItem: {'value': str},
        SwitchItem: {'value': str},
        ContactItem: {'value': str},
        PlayerItem: {'value': str},

        NumberItem:        {'value': Union[int, float]},
        RollershutterItem: {'value': Union[int, float]},
        DimmerItem:        {'value': Union[int, float]},

        ColorItem: {'value': Tuple[float, float, float]},
        CallItem: {'value': Tuple[str, ...]},
        LocationItem: {'value': Optional[Tuple[float, float, Optional[float]]]},

        DatetimeItem: {'value': datetime},
        ImageItem: {'value': bytes},

        GroupItem: {'value': Any}
    }

    init_missing = {
        **{k: ('last_change', 'last_update') for k in correct_hints},
        ImageItem: ('image_type', 'last_change', 'last_update'),
        ColorItem: ('value', 'last_change', 'last_update')
    }

    init_alias = {
        **{k: {'initial_value': 'value'} for k in correct_hints},
        ColorItem: {'b': 'brightness', 'h': 'hue', 's': 'saturation'}
    }

    class_vars = check_class_annotations(
        cls, correct_hints.get(cls),
        init_alias=init_alias.get(cls), init_missing=init_missing.get(cls, []),
        annotations_missing=True
    )

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
    target_vars = get_ivars_from_docstring(OpenhabItem)
    target_vars.pop('value')
    assert target_vars == class_vars
