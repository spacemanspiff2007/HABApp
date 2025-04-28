from unittest.mock import MagicMock

import pytest

from HABApp.core.events import NoEventFilter, ValueChangeEvent, ValueUpdateEvent
from HABApp.core.items import ColorItem
from HABApp.core.types import HSB, RGB
from tests.helpers import TestEventBus


def test_repr() -> None:
    str(ColorItem('test'))


def test_init() -> None:
    v = HSB(0, 1, 2)
    assert ColorItem('', v).hue == 0
    assert ColorItem('', v).saturation == 1
    assert ColorItem('', v).brightness == 2
    assert ColorItem('', v).value == HSB(0, 1, 2)

@pytest.mark.parametrize('func_name', ['set_value', 'post_value'])
@pytest.mark.parametrize(
    'test_vals', [
        ((45, 46, 47), HSB(45, 46, 47)),
        (HSB(45, 46, 47), HSB(45, 46, 47)),
        (RGB(168, 123, 94), RGB(168, 123, 94).to_hsb()),
    ]
)
def test_set_func_vals(func_name, test_vals) -> None:
    i = ColorItem('test', HSB(hue=11.11, saturation=22.22, brightness=33.33))
    assert i.hue == 11.11
    assert i.saturation == 22.22
    assert i.brightness == 33.33
    assert i.value == HSB(11.11, 22.22, 33.33)

    arg, soll = test_vals
    getattr(i, func_name)(arg)

    h, s, b = soll
    assert i.hue == h
    assert i.saturation == s
    assert i.brightness == b
    assert i.value == soll


def test_set_func_tuple() -> None:
    i = ColorItem('test', HSB(0, 0, 0))
    assert i.hue == 0
    assert i.saturation == 0
    assert i.brightness == 0

    i.set_value((22, 33.3, 77))

    assert i.hue == 22
    assert i.saturation == 33.3
    assert i.brightness == 77
    assert i.value == HSB(22, 33.3, 77)


def test_rgb_to_hsv() -> None:
    i = ColorItem('test')
    i.set_value(RGB(193, 25, 99))

    assert int(i.hue) == 333
    assert int(i.saturation) == 87
    assert int(i.brightness) == 75
    assert HSB(*[int(v) for v in i.value]) == HSB(333, 87, 75)


def test_hsv_to_rgb() -> None:
    i = ColorItem('test', HSB(23, 44, 66))
    assert i.get_rgb() == RGB(168, 123, 94)


def test_post_update(sync_worker, eb: TestEventBus) -> None:
    i = ColorItem('test', HSB(23, 44, 66))

    mock = MagicMock()
    eb.listen_events(i.name, mock, NoEventFilter())
    mock.assert_not_called()

    i.post_value(HSB(1, 2, 3))
    mock.assert_called()

    update = mock.call_args_list[0][0][0]
    assert isinstance(update, ValueUpdateEvent)
    assert update.name == 'test'
    assert update.value == HSB(1, 2, 3)

    update = mock.call_args_list[1][0][0]
    assert isinstance(update, ValueChangeEvent)
    assert update.name == 'test'
    assert update.value == HSB(1, 2, 3)
    assert update.old_value == HSB(23, 44, 66)
