from unittest.mock import Mock

import pytest

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.core.internals import EventBus
from HABApp.openhab.items import DimmerItem


def test_dimmer_item_bool() -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert not DimmerItem('asdf', event_bus=Mock(EventBus))

    assert not DimmerItem('asdf', 0, event_bus=Mock(EventBus))
    assert DimmerItem('asdf', 1, event_bus=Mock(EventBus))


def test_dimmer_set_value() -> None:
    DimmerItem('', event_bus=Mock(EventBus)).set_value(None)
    DimmerItem('', event_bus=Mock(EventBus)).set_value(0)
    DimmerItem('', event_bus=Mock(EventBus)).set_value(100)
    DimmerItem('', event_bus=Mock(EventBus)).set_value(55.55)

    with pytest.raises(InvalidItemValueError):
        DimmerItem('item_name', event_bus=Mock(EventBus)).set_value('asdf')


def test_switch_post_update(websocket_events) -> None:
    sw = DimmerItem('', event_bus=Mock(EventBus))

    sw.oh_post_update('ON')
    websocket_events.assert_called_once('OnOff', 'ON', event='update')
