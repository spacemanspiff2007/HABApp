import inspect
from datetime import datetime
from typing import Any

import pytest

from HABApp.core.items import Item
from HABApp.core.types import HSB
from HABApp.openhab.definitions import UnDefType
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
from HABApp.openhab.types import RawType

from ...helpers.inspect import assert_same_signature, check_class_annotations, get_ivars_from_docstring


@pytest.mark.parametrize('cls', (c for c in item_dict.values()))
def test_argspec_from_oh(cls) -> None:
    target_spec = inspect.getfullargspec(OpenhabItem.from_oh)
    current_spec = inspect.getfullargspec(cls.from_oh)
    assert current_spec == target_spec


@pytest.mark.parametrize('cls', tuple(c for c in item_dict.values()) + (Thing, ))
def test_set_name(cls) -> None:

    # test that we can set the name properly
    c = cls('asdf')
    assert c.name == 'asdf'

    # this test ensures that all openHAB items inherit from OpenhabItem
    if cls is not Thing:
        assert isinstance(c, OpenhabItem)


@pytest.mark.parametrize('cls', (c for c in item_dict.values()))
def test_conditional_function_call_signature(cls) -> None:
    assert_same_signature(Item.post_value_if, cls.post_value_if)
    assert_same_signature(Item.post_value_if, cls.oh_post_update_if)


@pytest.mark.parametrize('cls', item_dict.values())
def test_refresh_command(cls: type[OpenhabItem], sent_commands) -> None:
    cls('name').oh_send_command('REFRESH')
    sent_commands.assert_called_with('REFRESH')
    cls('name').command_value('REFRESH')
    sent_commands.assert_called_with('REFRESH')


@pytest.mark.parametrize('cls', item_dict.values())
def test_null_update(cls: type[OpenhabItem], posted_updates) -> None:
    cls('name').oh_post_update(None)
    posted_updates.assert_called_with(UnDefType.NULL)


@pytest.mark.parametrize('cls', item_dict.values())
def test_item_name_set_in_oh_value(cls: type[OpenhabItem]) -> None:
    assert cls._update_to_oh._name == cls.__name__
    assert cls._command_to_oh._name == cls.__name__


@pytest.mark.parametrize('cls', (c for c in item_dict.values()))
def test_doc_ivar(cls) -> None:

    correct_hints = {
        StringItem: {'value': str},
        SwitchItem: {'value': str},
        ContactItem: {'value': str},
        PlayerItem: {'value': str},

        NumberItem:        {'value': int | float},
        RollershutterItem: {'value': int | float},
        DimmerItem:        {'value': int | float},

        ColorItem: {'value': HSB},
        CallItem: {'value': tuple[str, ...]},
        LocationItem: {'value': tuple[float, float, float | None]},

        DatetimeItem: {'value': datetime},
        ImageItem: {'value': RawType},

        GroupItem: {'value': Any}
    }

    init_missing = {
        **{k: ('last_change', 'last_update') for k in correct_hints},
        ImageItem: ('image_type', 'last_change', 'last_update'),
        ColorItem: ('hue', 'saturation', 'brightness', 'last_change', 'last_update')
    }

    init_alias = {
        **{k: {'initial_value': 'value'} for k in correct_hints},
    }

    class_vars = check_class_annotations(
        cls, correct_hints.get(cls),
        init_alias=init_alias.get(cls), init_missing=init_missing.get(cls, []),
        annotations_missing=True, ignore=('_update_to_oh', '_command_to_oh', '_state_from_oh_str')
    )

    # test that the class has the corresponding attribute
    create_with = {'name': 'test'}

    if cls is ColorItem:
        create_with['initial_value'] = HSB(0, 0, 0)

    obj = cls(**create_with)
    for name in class_vars:
        assert hasattr(obj, name)

    if cls is ImageItem:
        class_vars.pop('image_type')

    class_vars.pop('value')

    # compare with base class so we have a consistent signature
    target_vars = get_ivars_from_docstring(OpenhabItem)
    target_vars.pop('value')
    assert target_vars == class_vars
