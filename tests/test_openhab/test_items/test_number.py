from unittest.mock import Mock

import pytest
from immutables import Map

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.core.internals import EventBus
from HABApp.openhab.items import NumberItem
from HABApp.openhab.items.base_item import MetaData


def test_number_item_unit(oh_interface) -> None:
    assert NumberItem('test', 1, event_bus=Mock(EventBus), interface=oh_interface).unit is None
    assert NumberItem('test', 1, metadata=Map(unit=MetaData('°C')), event_bus=Mock(EventBus), interface=oh_interface).unit == '°C'


def test_number_item_bool(oh_interface) -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert not NumberItem('asdf', event_bus=Mock(EventBus), interface=oh_interface)

    assert not NumberItem('asdf', 0, event_bus=Mock(EventBus), interface=oh_interface)
    assert NumberItem('asdf', 1, event_bus=Mock(EventBus), interface=oh_interface)


def test_number_set_value(oh_interface) -> None:
    NumberItem('', event_bus=Mock(EventBus), interface=oh_interface).set_value(None)
    NumberItem('', event_bus=Mock(EventBus), interface=oh_interface).set_value(1)
    NumberItem('', event_bus=Mock(EventBus), interface=oh_interface).set_value(-3.3)

    with pytest.raises(InvalidItemValueError):
        NumberItem('item_name', event_bus=Mock(EventBus), interface=oh_interface).set_value('asdf')
