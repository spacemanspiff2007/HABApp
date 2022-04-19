import pytest

from HABApp.openhab.errors import SendCommandNotSupported
from HABApp.openhab.items import ContactItem


def test_send_command():
    c = ContactItem('item_name')

    with pytest.raises(SendCommandNotSupported) as e:
        c.oh_send_command('asdf')

    assert str(e.value) == 'ContactItem does not support send command! See openHAB documentation for details.'
