import logging
from unittest.mock import Mock

import pytest

from HABApp.core.errors import InvalidItemValueError
from HABApp.core.internals import EventBus
from HABApp.openhab.items import ContactItem


def test_send_command() -> None:
    c = ContactItem('item_name', event_bus=Mock(EventBus))

    with pytest.raises(ValueError) as e:
        c.oh_send_command('asdf')
    assert str(e.value) == "Invalid value: 'asdf' (<class 'str'>) for ContactItem"


def test_switch_set_value() -> None:
    ContactItem('', event_bus=Mock(EventBus)).set_value(None)
    ContactItem('', event_bus=Mock(EventBus)).set_value('OPEN')
    ContactItem('', event_bus=Mock(EventBus)).set_value('CLOSED')

    with pytest.raises(InvalidItemValueError):
        ContactItem('item_name', event_bus=Mock(EventBus)).set_value('asdf')


def test_from_oh_str(caplog) -> None:
    assert ContactItem._state_from_oh_str('OPEN') == 'OPEN'
    assert ContactItem._state_from_oh_str_or_none('item_name', 'OPEN') == 'OPEN'
    assert ContactItem._state_from_oh_str_or_none('item_name', 'invalid', logging.getLogger('oh_str').warning) is None

    assert caplog.messages == ['Invalid value for ContactItem item_name: "invalid"! Using None instead']
    caplog.clear()
