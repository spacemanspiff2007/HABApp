import pytest

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
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

    with pytest.raises(InvalidItemValueError):
        SwitchItem('item_name').set_value('asdf')


def test_switch_post_update(posted_updates) -> None:
    sw = SwitchItem('')

    sw.oh_post_update('ON')
    posted_updates.assert_called_with('ON')

    sw.oh_post_update('OFF')
    posted_updates.assert_called_with('OFF')
