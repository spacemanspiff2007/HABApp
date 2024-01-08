import pytest

from HABApp.core.errors import InvalidItemValue
from HABApp.openhab.errors import SendCommandNotSupported
from HABApp.openhab.items import ContactItem


def test_send_command():
    c = ContactItem('item_name')

    with pytest.raises(SendCommandNotSupported) as e:
        c.oh_send_command('asdf')

    assert str(e.value) == 'ContactItem does not support send command! See openHAB documentation for details.'


def test_switch_set_value():
    ContactItem('').set_value(None)
    ContactItem('').set_value('OPEN')
    ContactItem('').set_value('CLOSED')

    with pytest.raises(InvalidItemValue):
        ContactItem('item_name').set_value('asdf')
