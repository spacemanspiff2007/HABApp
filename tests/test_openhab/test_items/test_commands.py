import pytest
import typing

from HABApp.openhab.items import ContactItem, DimmerItem, RollershutterItem, SwitchItem, ColorItem, \
    DatetimeItem, GroupItem, LocationItem, NumberItem, PlayerItem, StringItem, ImageItem
from HABApp.openhab.definitions import OnOffValue, UpDownValue, OpenClosedValue
from HABApp.openhab.items.commands import UpDownCommand, OnOffCommand

ALL_ITEMS = [
    ContactItem, DimmerItem, RollershutterItem, SwitchItem, ColorItem, ImageItem,
    DatetimeItem, GroupItem, LocationItem, NumberItem, PlayerItem, StringItem
]


@pytest.mark.parametrize("cls", [cls for cls in ALL_ITEMS if issubclass(cls, OnOffCommand)])
def test_OnOff(cls):
    c = cls('item_name')
    c.set_value(OnOffValue('ON'))
    assert c.is_on()
    assert not c.is_off()

    c = cls('item_name')
    c.set_value(OnOffValue('OFF'))
    assert c.is_off()
    assert not c.is_on()


@pytest.mark.parametrize("cls", [cls for cls in ALL_ITEMS if issubclass(cls, UpDownCommand)])
def test_UpDown(cls):
    c = cls('item_name')
    c.set_value(UpDownValue('UP'))
    assert c.is_up()
    assert not c.is_down()

    c = cls('item_name')
    c.set_value(UpDownValue('DOWN'))
    assert not c.is_up()
    assert c.is_down()


@pytest.mark.parametrize("cls", (ContactItem, ))
def test_OpenClosed(cls: typing.Type[ContactItem]):
    c = cls('item_name')
    c.set_value(OpenClosedValue.OPEN)
    assert c.is_open()
    assert not c.is_closed()

    c = cls('item_name')
    c.set_value(OpenClosedValue.CLOSED)
    assert c.is_closed()
    assert not c.is_open()
