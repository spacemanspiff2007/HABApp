from unittest.mock import Mock

import pytest

from HABApp.core.errors import ItemNameNotOfTypeStrError, WrongItemTypeError
from HABApp.core.internals import ItemRegistry
from HABApp.core.items import BaseItem, BaseValueItem
from HABApp.core.provider import HabAppObjProvider
from HABApp.mqtt import MqttInterface
from HABApp.mqtt.items import MqttBaseItem, MqttPairItem
from HABApp.openhab.items import OpenhabItem
from tests.helpers.inspect import get_module_classes


def get_item_classes() -> list[type[BaseValueItem]]:
    classes = []
    for module_name in ('core', 'openhab', 'mqtt'):

        for cls in get_module_classes(
                f'HABApp.{module_name}.items', exclude=(MqttBaseItem, ), subclass=BaseValueItem, include_subclass=False
        ).values():

            classes.append(cls)

    return classes


def params_item_init():
    params = []
    for cls in get_item_classes():
        kwargs = {}

        if issubclass(cls, MqttBaseItem):
            kwargs = {'interface': Mock(MqttInterface)}

        params.append(
            pytest.param(cls, kwargs, id=f'{cls.__module__.rsplit('.', 1)[-1]}.{cls.__name__}')
        )
    return params


@pytest.mark.parametrize(('cls', 'kwargs'), params_item_init())
def test_item_init(cls: type[BaseValueItem], kwargs: dict) -> None:

    # test normal create
    item = cls('item_name', **kwargs)
    assert item.name == 'item_name'
    assert item.value is None

    # test create positional
    item = cls(name='item_name', **kwargs)
    assert item.name == 'item_name'
    assert item.value is None


def params_get_create_item():

    params = []
    for cls in get_item_classes():
        if issubclass(cls, OpenhabItem):
            continue

        kwargs = {}
        if issubclass(cls, MqttPairItem):
            kwargs = {'write_topic': 'write_topic'}

        params.append(
            pytest.param(cls, kwargs, id=f'{cls.__module__.rsplit('.', 1)[-1]}.{cls.__name__}')
        )
    return params


def _setup_item(cls: type, monkeypatch: pytest.MonkeyPatch, ir: ItemRegistry) -> None:
    provider_objs = {ItemRegistry: ir, MqttInterface: Mock(MqttInterface)}
    provider_mock = Mock(HabAppObjProvider)
    provider_mock.get_existing = Mock(side_effect=provider_objs.__getitem__)

    # Provider for get_item()
    monkeypatch.setattr(BaseItem.__module__ + '.HABAPP_PROVIDER', provider_mock)

    # Provider for get_create_item
    if not issubclass(cls, OpenhabItem):
        monkeypatch.setattr(cls.__module__ + '.HABAPP_PROVIDER', provider_mock)


@pytest.mark.parametrize(('cls', 'kwargs'), params_get_create_item())
def test_get_create_item(cls: type[BaseValueItem], kwargs: dict, monkeypatch, ir) -> None:
    _setup_item(cls, monkeypatch, ir)

    with pytest.raises(ItemNameNotOfTypeStrError):
        cls.get_create_item(name=123)

    # test normal create
    item = cls.get_create_item('item_name', **kwargs)
    assert item.name == 'item_name'
    assert item.value is None

    # check that is was properly created
    assert ir.get_item('item_name') is item

    # test create positional
    item2 = cls.get_create_item(name='item_name', **kwargs)
    assert item2 is item


@pytest.mark.parametrize(('cls', 'kwargs'), params_item_init())
def test_get_item(cls: type[BaseValueItem], kwargs: dict, monkeypatch, ir) -> None:
    _setup_item(cls, monkeypatch, ir)

    with pytest.raises(ItemNameNotOfTypeStrError):
        cls.get_item(name=123)

    ir.add_item(BaseValueItem('item_name'))

    with pytest.raises(WrongItemTypeError):
        cls.get_item(name='item_name')

    ir.pop_item('item_name')

    # test normal create
    item = cls('item_name', **kwargs)
    ir.add_item(item)

    # test create positional
    item2 = cls.get_item(name='item_name')
    assert item2 is item
