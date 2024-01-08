import pytest

from HABApp.core.errors import InvalidItemValue, ItemValueIsNoneError
from HABApp.openhab.items import DimmerItem


def test_dimmer_item_bool():
    with pytest.raises(ItemValueIsNoneError):
        assert not DimmerItem('asdf')

    assert not DimmerItem('asdf', 0)
    assert DimmerItem('asdf', 1)


def test_dimmer_set_value():
    DimmerItem('').set_value(None)
    DimmerItem('').set_value(0)
    DimmerItem('').set_value(100)
    DimmerItem('').set_value(55.55)

    with pytest.raises(InvalidItemValue):
        DimmerItem('item_name').set_value('asdf')
