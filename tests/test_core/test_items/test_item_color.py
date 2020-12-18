from unittest.mock import MagicMock

import pytest

from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.items import ColorItem
from ...helpers import TestEventBus


def test_repr():
    str(ColorItem('test'))


def test_init():
    assert ColorItem('').hue == 0
    assert ColorItem('').saturation == 0
    assert ColorItem('').brightness == 0

    assert ColorItem('', hue=11).hue == 11
    assert ColorItem('', hue=11).value == (11, 0, 0)
    assert ColorItem('', saturation=33).saturation == 33
    assert ColorItem('', saturation=33).value == (0, 33, 0)
    assert ColorItem('', brightness=22).brightness == 22
    assert ColorItem('', brightness=22).value == (0, 0, 22)


@pytest.mark.parametrize("func_name", ['set_value', 'post_value'])
@pytest.mark.parametrize(
    "test_vals", [
        ((45, 46, 47), (45, 46, 47)),
        ((10, None, None), (10, 22.22, 33.33)),
        ((None, 50, None), (11.11, 50, 33.33)),
        ((None, None, 60), (11.11, 22.22, 60)),
    ]
)
def test_set_func_vals(func_name, test_vals):
    i = ColorItem('test', hue=11.11, saturation=22.22, brightness=33.33)
    assert i.hue == 11.11
    assert i.saturation == 22.22
    assert i.brightness == 33.33
    assert i.value == (11.11, 22.22, 33.33)

    arg, soll = test_vals

    getattr(i, func_name)(*arg)

    assert i.hue == soll[0]
    assert i.saturation == soll[1]
    assert i.brightness == soll[2]
    assert i.value == soll


def test_set_func_tuple():
    i = ColorItem('test')
    assert i.hue == 0
    assert i.saturation == 0
    assert i.brightness == 0

    i.set_value((22, 33.3, 77))

    assert i.hue == 22
    assert i.saturation == 33.3
    assert i.brightness == 77
    assert i.value == (22, 33.3, 77)


def test_rgb_to_hsv():
    i = ColorItem('test')
    i.set_rgb(193, 25, 99)

    assert int(i.hue) == 333
    assert int(i.saturation) == 87
    assert int(i.brightness) == 75
    assert tuple(int(i) for i in i.value) == (333, 87, 75)


def test_hsv_to_rgb():
    i = ColorItem('test', 23, 44, 66)
    assert i.get_rgb() == (168, 122, 94)


def test_post_update(sync_worker, event_bus: TestEventBus):
    i = ColorItem('test', 23, 44, 66)

    mock = MagicMock()
    event_bus.listen_events(i.name, mock)
    mock.assert_not_called()

    i.post_value(1, 2, 3)
    mock.assert_called()

    update = mock.call_args_list[0][0][0]
    assert isinstance(update, ValueUpdateEvent)
    assert update.name == 'test'
    assert update.value == (1, 2, 3)

    update = mock.call_args_list[1][0][0]
    assert isinstance(update, ValueChangeEvent)
    assert update.name == 'test'
    assert update.value == (1, 2, 3)
    assert update.old_value == (23, 44, 66)
