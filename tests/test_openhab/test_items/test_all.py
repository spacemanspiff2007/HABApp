import inspect
from datetime import datetime
from typing import Any, Literal
from unittest.mock import Mock

import pytest

from HABApp.core.internals import EventBus
from HABApp.core.items import Item
from HABApp.core.types import HSB, Point
from HABApp.openhab.item_factory import OhItemFactory
from HABApp.openhab.item_registry_handler import OhItemRegistryHandler
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
from HABApp.openhab.types import RawType, StringList
from tests.helpers.inspect import assert_same_signature, check_class_annotations, get_ivars_from_docstring


def _get_oh_classes() -> tuple[type[OpenhabItem], ...]:
    return tuple(c for c in OhItemFactory(None, None, None)._items.values())


@pytest.fixture(params=_get_oh_classes())
def cls(request):
    return request.param


@pytest.fixture
def cls_instance(cls, eb, oh_interface):
    kwargs = {'event_bus': eb, 'interface': oh_interface}
    if issubclass(cls, GroupItem):
        kwargs['registry_handler'] = Mock(OhItemRegistryHandler)
    return cls('item_name', **kwargs)


def test_name(cls_instance) -> None:
    assert cls_instance.name == 'item_name'


def test_thing_name(oh_interface) -> None:
    t = Thing('thing_name', interface=oh_interface)
    assert t.name == 'thing_name'


def test_inheritance(cls_instance) -> None:
    # all items must inherit from OpenhabItem
    assert isinstance(cls_instance, OpenhabItem)


def test_conditional_function_call_signature(cls) -> None:
    p = [inspect.Parameter('source', inspect.Parameter.KEYWORD_ONLY, default=None, annotation=str | None)]

    assert_same_signature(Item.post_value_if, cls.post_value_if, drop_params=p)
    assert_same_signature(Item.post_value_if, cls.oh_post_update_if, drop_params=p)


def test_refresh_command(cls_instance: OpenhabItem, websocket_events) -> None:
    cls_instance.oh_send_command('REFRESH')
    websocket_events.assert_called_once('Refresh', 'REFRESH', event='command')
    cls_instance.command_value('REFRESH')
    websocket_events.assert_called_once('Refresh', 'REFRESH', event='command')


def test_null_update(cls_instance: OpenhabItem, websocket_events) -> None:
    cls_instance.oh_post_update(None)
    websocket_events.assert_called_once('UnDef', 'NULL', event='update')


def test_item_name_set_in_oh_value(cls: type[OpenhabItem]) -> None:
    assert cls._update_to_oh._name == cls.__name__
    assert cls._command_to_oh._name == cls.__name__


def test_doc_ivar(cls, oh_interface) -> None:

    correct_hints = {
        StringItem: {'value': str},
        SwitchItem: {'value': Literal['ON', 'OFF']},
        ContactItem: {'value': Literal['OPEN', 'CLOSED']},
        PlayerItem: {'value': str},

        NumberItem:        {'value': int | float},
        RollershutterItem: {'value': int | float},
        DimmerItem:        {'value': int | float},

        ColorItem: {'value': HSB},
        CallItem: {'value': StringList},
        LocationItem: {'value': Point},

        DatetimeItem: {'value': datetime},
        ImageItem: {'value': RawType},

        GroupItem: {'value': Any}
    }

    # last_value must have the same hint
    for k, v in correct_hints.items():
        v['last_value'] = v['value']

    init_missing = {
        **{k: ('last_change', 'last_update') for k in correct_hints},
        ImageItem: ('image_type', 'image_data', 'last_change', 'last_update'),
        ColorItem: ('hue', 'saturation', 'brightness', 'last_change', 'last_update')
    }

    init_alias = {
        **{k: {'initial_value': 'value'} for k in correct_hints},
    }

    class_vars = check_class_annotations(
        cls, correct_hints.get(cls),
        init_alias=init_alias.get(cls), init_missing=init_missing.get(cls, []),
        annotations_missing=True,
        ignore=(
            '_update_to_oh', '_command_to_oh', '_state_from_oh_str',
            # class specific
            'registry_handler', 'event_bus', 'interface',
        )
    )

    # test that the class has the corresponding attribute
    create_with = {'name': 'test', 'event_bus': Mock(EventBus), 'interface': oh_interface}

    if cls is ColorItem:
        create_with['initial_value'] = HSB(0, 0, 0)
    if cls is ImageItem:
        create_with['initial_value'] = RawType.create('image/png', b'\x01')
    if cls is GroupItem:
        create_with['registry_handler'] = Mock(OhItemRegistryHandler)

    obj = cls(**create_with)
    for name in class_vars:
        assert hasattr(obj, name)

    class_vars.pop('value')
    class_vars.pop('last_value')

    if cls is NumberItem:
        class_vars.pop('dimension')

    # compare with base class so we have a consistent signature
    target_vars = get_ivars_from_docstring(OpenhabItem)
    target_vars.pop('value')
    target_vars.pop('last_value')

    assert target_vars == class_vars
