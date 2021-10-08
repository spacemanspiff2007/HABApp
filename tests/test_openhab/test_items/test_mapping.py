from HABApp.openhab.map_items import map_item
from HABApp.openhab.items import NumberItem, DatetimeItem
from datetime import datetime


def test_exception():
    assert map_item('test', 'Number', 'asdf', frozenset(), frozenset()) is None


def test_number_unit_of_measurement():
    assert map_item('test1', 'Number:Length', '1.0 m', frozenset(), frozenset()) == NumberItem('test', 1)
    assert map_item('test2', 'Number:Temperature', '2.0 °C', frozenset(), frozenset()) == NumberItem('test', 2)
    assert map_item('test3', 'Number:Pressure', '3.0 hPa', frozenset(), frozenset()) == NumberItem('test', 3)
    assert map_item('test4', 'Number:Speed', '4.0 km/h', frozenset(), frozenset()) == NumberItem('test', 4)
    assert map_item('test5', 'Number:Intensity', '5.0 W/m2', frozenset(), frozenset()) == NumberItem('test', 5)
    assert map_item('test6', 'Number:Dimensionless', '6.0', frozenset(), frozenset()) == NumberItem('test', 6)
    assert map_item('test7', 'Number:Angle', '7.0 °', frozenset(), frozenset()) == NumberItem('test', 7)


def test_datetime():
    # Todo: remove this test once we go >= OH3.1
    # Old format
    assert map_item('test1', 'DateTime', '2018-11-19T09:47:38.284+0000', frozenset(), frozenset()) == \
           DatetimeItem('test', datetime(2018, 11, 19,  9, 47, 38, 284000)) or \
           DatetimeItem('test', datetime(2018, 11, 19, 10, 47, 38, 284000))

    # From >= OH3.1
    assert map_item('test1', 'DateTime', '2021-04-10T21:00:43.043996+0000', frozenset(), frozenset()) == \
           DatetimeItem('test', datetime(2021, 4, 10, 21, 0, 43, 43996)) or \
           DatetimeItem('test', datetime(2021, 4, 10, 23, 0, 43, 43996))
