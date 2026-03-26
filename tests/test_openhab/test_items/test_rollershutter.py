from unittest.mock import Mock

import pytest

from HABApp.core.errors import InvalidItemValueError
from HABApp.core.internals import EventBus
from HABApp.openhab.items import RollershutterItem


def test_dimmer_set_value() -> None:
    RollershutterItem('', event_bus=Mock(EventBus)).set_value(None)
    RollershutterItem('', event_bus=Mock(EventBus)).set_value(0)
    RollershutterItem('', event_bus=Mock(EventBus)).set_value(100)
    RollershutterItem('', event_bus=Mock(EventBus)).set_value(55.55)

    with pytest.raises(InvalidItemValueError):
        RollershutterItem('item_name', event_bus=Mock(EventBus)).set_value('asdf')
