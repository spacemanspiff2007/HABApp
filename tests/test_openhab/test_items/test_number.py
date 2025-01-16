import pytest
from immutables import Map

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.openhab.items import NumberItem
from HABApp.openhab.items.base_item import MetaData


def test_number_item_unit() -> None:
    assert NumberItem('test', 1).unit is None
    assert NumberItem('test', 1, metadata=Map(unit=MetaData('°C'))).unit == '°C'


def test_number_item_bool() -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert not NumberItem('asdf')

    assert not NumberItem('asdf', 0)
    assert NumberItem('asdf', 1)


def test_number_set_value() -> None:
    NumberItem('').set_value(None)
    NumberItem('').set_value(1)
    NumberItem('').set_value(-3.3)

    with pytest.raises(InvalidItemValueError):
        NumberItem('item_name').set_value('asdf')
