import typing

import pytest

from HABApp import __version__
from HABApp.openhab.definitions import OnOffValue, OpenClosedValue, UpDownValue
from HABApp.openhab.items import ContactItem
from HABApp.openhab.items.commands import OnOffCommand, UpDownCommand
from HABApp.openhab.map_items import _items as item_dict


@pytest.mark.parametrize('cls', [cls for cls in item_dict.values() if issubclass(cls, OnOffCommand)])
def test_OnOff(cls):
    c = cls('item_name')
    assert not c.is_on()
    if not __version__.startswith('24.08.0'):
        assert not c.is_off()

    c.set_value(OnOffValue('ON'))
    assert c.is_on()
    assert not c.is_off()

    c = cls('item_name')
    c.set_value(OnOffValue('OFF'))
    assert c.is_off()
    assert not c.is_on()


@pytest.mark.parametrize('cls', [cls for cls in item_dict.values() if issubclass(cls, UpDownCommand)])
def test_UpDown(cls):
    c = cls('item_name')
    c.set_value(UpDownValue('UP'))
    assert c.is_up()
    assert not c.is_down()

    c = cls('item_name')
    c.set_value(UpDownValue('DOWN'))
    assert not c.is_up()
    assert c.is_down()


@pytest.mark.parametrize('cls', (ContactItem, ))
def test_OpenClosed(cls: typing.Type[ContactItem]):
    c = cls('item_name')
    assert not c.is_closed()
    assert not c.is_open()

    c.set_value(OpenClosedValue.OPEN)
    assert c.is_open()
    assert not c.is_closed()

    c = cls('item_name')
    c.set_value(OpenClosedValue.CLOSED)
    assert c.is_closed()
    assert not c.is_open()
