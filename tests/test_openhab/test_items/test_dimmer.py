import pytest

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.openhab.items import DimmerItem


def test_dimmer_item_bool() -> None:
    with pytest.raises(ItemValueIsNoneError):
        assert not DimmerItem('asdf')

    assert not DimmerItem('asdf', 0)
    assert DimmerItem('asdf', 1)


def test_dimmer_set_value() -> None:
    DimmerItem('').set_value(None)
    DimmerItem('').set_value(0)
    DimmerItem('').set_value(100)
    DimmerItem('').set_value(55.55)

    with pytest.raises(InvalidItemValueError):
        DimmerItem('item_name').set_value('asdf')


def test_switch_post_update(websocket_events) -> None:
    sw = DimmerItem('')

    sw.oh_post_update('ON')
    websocket_events.assert_called_once('OnOff', 'ON', event='update')
