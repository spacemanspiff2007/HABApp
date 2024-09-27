import pytest

from HABApp.core.errors import InvalidItemValue, ItemValueIsNoneError
from HABApp.openhab.items import SwitchItem


def test_switch_item_bool() -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert SwitchItem('test')

    assert not SwitchItem('test', 'OFF')
    assert SwitchItem('test', 'ON')


def test_switch_set_value() -> None:
    SwitchItem('').set_value(None)
    SwitchItem('').set_value('ON')
    SwitchItem('').set_value('OFF')

    with pytest.raises(InvalidItemValue):
        SwitchItem('item_name').set_value('asdf')
