from immutables import Map

from HABApp.openhab.items import NumberItem
from HABApp.openhab.items.base_item import MetaData


def test_number_item_unit():
    assert NumberItem('test', 1).unit is None
    assert NumberItem('test', 1, metadata=Map(unit=MetaData('°C'))).unit == '°C'


def test_small_values():
    assert NumberItem('test', 1).unit is None
    assert NumberItem('test', 1, metadata=Map(unit=MetaData('°C'))).unit == '°C'
