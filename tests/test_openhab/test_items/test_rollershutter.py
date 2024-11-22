import pytest

from HABApp.core.errors import InvalidItemValue
from HABApp.openhab.items import RollershutterItem


def test_dimmer_set_value() -> None:
    RollershutterItem('').set_value(None)
    RollershutterItem('').set_value(0)
    RollershutterItem('').set_value(100)
    RollershutterItem('').set_value(55.55)

    with pytest.raises(InvalidItemValue):
        RollershutterItem('item_name').set_value('asdf')
