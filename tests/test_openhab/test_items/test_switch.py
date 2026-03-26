from unittest.mock import Mock

import pytest

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.core.internals import EventBus
from HABApp.openhab.items import SwitchItem


def test_switch_item_bool() -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert SwitchItem('test', event_bus=Mock(EventBus))

    assert not SwitchItem('test', 'OFF', event_bus=Mock(EventBus))
    assert SwitchItem('test', 'ON', event_bus=Mock(EventBus))


def test_switch_set_value() -> None:
    SwitchItem('', event_bus=Mock(EventBus)).set_value(None)
    SwitchItem('', event_bus=Mock(EventBus)).set_value('ON')
    SwitchItem('', event_bus=Mock(EventBus)).set_value('OFF')

    with pytest.raises(InvalidItemValueError):
        SwitchItem('item_name', event_bus=Mock(EventBus)).set_value('asdf')


def test_switch_post_update(websocket_events) -> None:
    sw = SwitchItem('', event_bus=Mock(EventBus))

    sw.oh_post_update('ON')
    websocket_events.assert_called_once('OnOff', 'ON', event='update')

    sw.oh_post_update('OFF')
    websocket_events.assert_called_once('OnOff', 'OFF', event='update')
