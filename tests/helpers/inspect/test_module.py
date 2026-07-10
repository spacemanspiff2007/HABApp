from HABApp.core import types as types_module
from HABApp.core.types import Point
from HABApp.core.types import color as color_module
from HABApp.core.types.color import HSB, RGB, RGB16, RGB24, RGB32, ColorType
from tests.helpers.inspect import get_module_classes


def test_get_color_module_classes() -> None:
    assert get_module_classes(color_module) == {
        'ColorType': ColorType, 'HSB': HSB, 'RGB': RGB, 'RGB16': RGB16, 'RGB24': RGB24, 'RGB32': RGB32
    }

    assert get_module_classes(color_module, subclass=RGB) == {
        'RGB': RGB, 'RGB16': RGB16, 'RGB24': RGB24, 'RGB32': RGB32
    }
    assert get_module_classes(color_module, subclass=RGB, include_subclass=False) == {
        'RGB16': RGB16, 'RGB24': RGB24, 'RGB32': RGB32
    }
    assert get_module_classes(color_module, subclass=RGB, include_subclass=False, exclude=(RGB16,)) == {
        'RGB24': RGB24, 'RGB32': RGB32
    }

    assert get_module_classes(color_module, subclass=(RGB16, RGB24, RGB32)) == {
        'RGB16': RGB16, 'RGB24': RGB24, 'RGB32': RGB32
    }


def test_get_type_module_classes() -> None:
    assert get_module_classes(types_module) == {
        'Point': Point, 'HSB': HSB, 'RGB': RGB, 'RGB16': RGB16, 'RGB24': RGB24, 'RGB32': RGB32
    }
    assert get_module_classes(types_module, include_imported=False) == {}
