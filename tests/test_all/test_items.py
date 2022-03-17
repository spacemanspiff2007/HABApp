import pytest

from HABApp.core.internals import BaseValueItem, TYPE_ITEM_CLS
from HABApp.mqtt.items import MqttBaseItem
from tests.helpers import get_module_classes


def get_item_classes(skip=tuple()):
    classes = []
    for module_name in ('core', 'openhab', 'mqtt'):
        if module_name in skip:
            continue

        for name, cls in get_module_classes(f'HABApp.{module_name}.items', exclude=[MqttBaseItem],
                                            subclass=BaseValueItem, include_subclass=False).items():
            if name in skip:
                continue

            default = None
            if name == 'ColorItem':
                default = (0.0, 0.0, 0.0)
            classes.append(pytest.param(cls, default, id=f'{module_name}.{cls.__name__}'))
    return classes


@pytest.mark.parametrize('item_cls, default', get_item_classes())
def test_create_item(item_cls: TYPE_ITEM_CLS, default):

    # test normal create
    item = item_cls('item_name')
    assert item.name == 'item_name'
    assert (item.value is None if default is None else item.value == default)

    # test create positional
    item = item_cls(name='item_name')
    assert item.name == 'item_name'
    assert (item.value is None if default is None else item.value == default)


@pytest.mark.parametrize(
    'item_cls, default', get_item_classes(skip=('openhab', 'MqttPairItem'),))
def test_get_create_item(item_cls: TYPE_ITEM_CLS, default):

    # test normal create
    item = item_cls.get_create_item('item_name')
    assert item.name == 'item_name'
    assert (item.value is None if default is None else item.value == default)

    # test create positional
    item2 = item_cls.get_create_item(name='item_name')
    assert item2 is item
