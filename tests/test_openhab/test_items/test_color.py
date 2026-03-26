import logging
from unittest.mock import Mock

import pytest

from HABApp.core.internals import EventBus
from HABApp.core.types import HSB
from HABApp.openhab.items import ColorItem


def test_send_command() -> None:
    c = ColorItem('item_name', event_bus=Mock(EventBus))

    with pytest.raises(ValueError) as e:
        c.oh_send_command('asdf')
    assert str(e.value) == "Invalid value: 'asdf' (<class 'str'>) for ColorItem"

    c.oh_send_command(HSB(1, 2, 3))


def test_from_oh_str(caplog) -> None:
    assert ColorItem._state_from_oh_str('1,2,3') == HSB(1, 2, 3)
    assert ColorItem._state_from_oh_str_or_none('item_name', '1,2,3') == HSB(1, 2, 3)
    assert ColorItem._state_from_oh_str_or_none('item_name', '0', logging.getLogger('oh_str').warning) is None

    assert caplog.messages == ['Invalid value for ColorItem item_name: "0"! Using None instead']
    caplog.clear()
