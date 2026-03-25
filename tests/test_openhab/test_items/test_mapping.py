from datetime import datetime
from functools import partial

import pytest
from immutables import Map
from whenever import SystemDateTime

from HABApp.openhab.item_factory import OhItemFactory
from HABApp.openhab.items import DatetimeItem, NumberItem
from HABApp.openhab.items.base_item import MetaData
from tests.helpers import TestEventBus


@pytest.mark.ignore_log_errors
def test_exception(eb: TestEventBus, item_factory: OhItemFactory) -> None:
    eb.allow_errors = True
    assert item_factory.create_item('test', 'Number', 'asdf', None, 'my_label', frozenset(), frozenset(), {}) is None


def test_metadata(item_factory: OhItemFactory) -> None:
    make_number = partial(item_factory.create_item, 'test', 'Number', None, None, 'my_label', frozenset(), frozenset())

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


def test_number_unit_of_measurement(item_factory: OhItemFactory) -> None:
    make_item = partial(
        item_factory.create_item,
        last_value=None, label='l', tags=frozenset(), groups=frozenset(), metadata={'unit': {'value': '°C'}}
    )
    metadata = Map(unit=MetaData('°C'))
    assert make_item('test1', 'Number:Length', '1.0 m', ) == NumberItem('test', 1, metadata=metadata)
    assert make_item('test2', 'Number:Temperature', '2.0 °C', ) == NumberItem('test', 2, metadata=metadata)
    assert make_item('test3', 'Number:Pressure', '3.0 hPa', ) == NumberItem('test', 3, metadata=metadata)
    assert make_item('test4', 'Number:Speed', '4.0 km/h', ) == NumberItem('test', 4, metadata=metadata)
    assert make_item('test5', 'Number:Intensity', '5.0 W/m2', ) == NumberItem('test', 5, metadata=metadata)
    assert make_item('test6', 'Number:Dimensionless', '6.0', ) == NumberItem('test', 6, metadata=metadata)
    assert make_item('test7', 'Number:Angle', '7.0 °', ) == NumberItem('test', 7, metadata=metadata)


def test_datetime(item_factory: OhItemFactory) -> None:

    # We have to build the offset str dynamically otherwise we will fail during CI because it's in another timezone
    offset_str = SystemDateTime(2022, 6, 15).format_common_iso()[-6:].replace(':', '')

    def get_dt(value: str):
        assert value.startswith('2022-06-15')   # Date must match with offset_str
        return item_factory.create_item(
            'test1', 'DateTime', f'{value}{offset_str}',
            label='', tags=frozenset(), groups=frozenset(), metadata={}, last_value=None
            )

    assert get_dt('2022-06-15T09:47:38.284') == datetime(2022, 6, 15,  9, 47, 38, 284000)
    assert get_dt('2022-06-15T09:21:43.043996') == datetime(2022, 6, 15,  9, 21, 43, 43996)
    assert get_dt('2022-06-15T09:21:43.754673068') == datetime(2022, 6, 15,  9, 21, 43, 754673)

    offset_str = '-0400'
    assert isinstance(get_dt('2022-06-15T09:21:43.754673068'), DatetimeItem)
