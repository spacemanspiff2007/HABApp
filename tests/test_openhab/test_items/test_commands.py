import typing

import pytest

from HABApp import __version__
from HABApp.core.types import HSB
from HABApp.openhab.definitions import OnOffValue, OpenClosedValue, UpDownValue, OpenClosedType, UpDownType
from HABApp.openhab.items import ContactItem, ColorItem
from HABApp.openhab.items.commands import OnOffCommand, UpDownCommand
from HABApp.openhab.map_items import _items as item_dict


@pytest.mark.parametrize('cls', [cls for cls in item_dict.values() if issubclass(cls, OnOffCommand)])
def test_OnOff(cls) -> None:
    c = cls('item_name')
    assert not c.is_on()
    assert not c.is_off()

    initial_value = None if cls is not ColorItem else HSB(0, 0, 0)
    c = cls('item_name', initial_value=initial_value)
    c.set_value(OnOffValue('ON'))
    assert c.is_on()
    assert not c.is_off()

    c = cls('item_name', initial_value=initial_value)
    c.set_value(OnOffValue('OFF'))
    assert c.is_off()
    assert not c.is_on()


@pytest.mark.parametrize('cls', [cls for cls in item_dict.values() if issubclass(cls, UpDownCommand)])
def test_UpDown(cls) -> None:
    c = cls('item_name')
    c.set_value(UpDownValue(UpDownType.UP))
    assert c.is_up()
    assert not c.is_down()

    c = cls('item_name')
    c.set_value(UpDownValue(UpDownType.DOWN))
    assert not c.is_up()
    assert c.is_down()


@pytest.mark.parametrize('cls', (ContactItem, ))
def test_OpenClosed(cls: type[ContactItem]) -> None:
    c = cls('item_name')
    assert not c.is_closed()
    assert not c.is_open()

    c.set_value(OpenClosedType.OPEN)
    assert c.is_open()
    assert not c.is_closed()

    c = cls('item_name')
    c.set_value(OpenClosedType.CLOSED)
    assert c.is_closed()
    assert not c.is_open()
