from unittest.mock import Mock

import pytest
from immutables import Map

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.core.internals import EventBus
from HABApp.openhab.items import NumberItem
from HABApp.openhab.items.base_item import MetaData


def test_number_item_unit() -> None:
    assert NumberItem('test', 1, event_bus=Mock(EventBus)).unit is None
    assert NumberItem('test', 1, metadata=Map(unit=MetaData('°C')), event_bus=Mock(EventBus)).unit == '°C'


def test_number_item_bool() -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert not NumberItem('asdf', event_bus=Mock(EventBus))

    assert not NumberItem('asdf', 0, event_bus=Mock(EventBus))
    assert NumberItem('asdf', 1, event_bus=Mock(EventBus))


def test_number_set_value() -> None:
    NumberItem('', event_bus=Mock(EventBus)).set_value(None)
    NumberItem('', event_bus=Mock(EventBus)).set_value(1)
    NumberItem('', event_bus=Mock(EventBus)).set_value(-3.3)

    with pytest.raises(InvalidItemValueError):
        NumberItem('item_name', event_bus=Mock(EventBus)).set_value('asdf')
