from inspect import signature
from typing import Any, get_args, get_origin

import pytest

from HABApp.openhab.definitions import values as values_module
from HABApp.openhab.definitions.values import ComplexOhValue
from tests.helpers.inspect import get_module_classes


def test_all_values():
    classes = get_module_classes(
        values_module, subclass=ComplexOhValue, include_subclass=False)

    for cls in classes.values():
        assert cls in values_module.ALL_VALUES

    assert len(classes) == len(values_module.ALL_VALUES)


@pytest.mark.parametrize('cls',  values_module.ALL_VALUES)
def test_hints(cls: type[ComplexOhValue]):
    s = signature(cls.__init__)
    assert 'value' in s.parameters

    init_anno = s.parameters['value'].annotation
    cls_anno = cls.__annotations__['value']

    if init_anno is Any:
        return None

    if get_origin(init_anno) is tuple:
        assert cls_anno in get_args(init_anno)
    else:
        assert init_anno is cls_anno
