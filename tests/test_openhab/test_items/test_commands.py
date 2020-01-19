import pytest
import typing

from HABApp.openhab.items import ContactItem, DimmerItem, RollershutterItem, SwitchItem, ColorItem
from HABApp.openhab.definitions import OnOffValue, UpDownValue, OpenClosedValue


@pytest.mark.parametrize("cls", (SwitchItem, DimmerItem, ColorItem))
def test_onoff(cls: typing.Type[SwitchItem]):
    c = cls('item_name')
    c.set_value(OnOffValue('ON'))
    assert c.is_on()
    assert not c.is_off()

    c = cls('item_name')
    c.set_value(OnOffValue('OFF'))
    assert c.is_off()
    assert not c.is_on()


@pytest.mark.parametrize("cls", (RollershutterItem, ))
def test_UpDown(cls: typing.Type[RollershutterItem]):
    c = cls('item_name')
    c.set_value(UpDownValue('UP'))

    c = cls('item_name')
    c.set_value(UpDownValue('DOWN'))


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
