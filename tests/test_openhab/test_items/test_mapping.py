from datetime import datetime
from functools import partial

from immutables import Map

from HABApp.openhab.items import DatetimeItem, NumberItem
from HABApp.openhab.map_items import map_item


def test_exception():
    assert map_item('test', 'Number', 'asdf', frozenset(), frozenset(), {}) is None


def test_metadata():
    make_number = partial(map_item, 'test', 'Number', None, frozenset(), frozenset())

    item = make_number({'ns1': {'value': 'v1'}})
    assert isinstance(item.metadata, Map)
    assert item.metadata['ns1'].value == 'v1'
    assert isinstance(item.metadata['ns1'].config, Map)
    assert item.metadata['ns1'].config == Map()

    item = make_number({'ns1': {'value': 'v1', 'config': {'c': 1}}})
    assert item.metadata['ns1'].value == 'v1'
    assert isinstance(item.metadata['ns1'].config, Map)
    assert item.metadata['ns1'].config == Map({'c': 1})

    item = make_number({'ns1': {'value': 'v1'}, 'ns2': {'value': 12}})
    assert item.metadata['ns1'].value == 'v1'
    assert item.metadata['ns1'].config == Map()
    assert item.metadata['ns2'].value == 12
    assert item.metadata['ns2'].config == Map()


def test_number_unit_of_measurement():
    make_item = partial(map_item, tags=frozenset(), groups=frozenset(), metadata={})
    assert make_item('test1', 'Number:Length', '1.0 m', ) == NumberItem('test', 1)
    assert make_item('test2', 'Number:Temperature', '2.0 °C', ) == NumberItem('test', 2)
    assert make_item('test3', 'Number:Pressure', '3.0 hPa', ) == NumberItem('test', 3)
    assert make_item('test4', 'Number:Speed', '4.0 km/h', ) == NumberItem('test', 4)
    assert make_item('test5', 'Number:Intensity', '5.0 W/m2', ) == NumberItem('test', 5)
    assert make_item('test6', 'Number:Dimensionless', '6.0', ) == NumberItem('test', 6)
    assert make_item('test7', 'Number:Angle', '7.0 °', ) == NumberItem('test', 7)


def test_datetime():
    # Todo: remove this test once we go >= OH3.1
    # Old format
    assert map_item('test1', 'DateTime', '2018-11-19T09:47:38.284+0000', frozenset(), frozenset(), {}) == \
           DatetimeItem('test', datetime(2018, 11, 19,  9, 47, 38, 284000)) or \
           DatetimeItem('test', datetime(2018, 11, 19, 10, 47, 38, 284000))

    # From >= OH3.1
    assert map_item('test1', 'DateTime', '2021-04-10T21:00:43.043996+0000', frozenset(), frozenset(), {}) == \
           DatetimeItem('test', datetime(2021, 4, 10, 21, 0, 43, 43996)) or \
           DatetimeItem('test', datetime(2021, 4, 10, 23, 0, 43, 43996))
