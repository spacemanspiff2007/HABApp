from datetime import datetime

import pytest

from HABApp.openhab.items import DatetimeItem, NumberItem
from HABApp.openhab.map_values import map_openhab_values


def test_type_none():
    assert map_openhab_values('UnDef', '0') is None
    assert map_openhab_values('Number', 'NULL') is None


@pytest.mark.parametrize('value, target', (('0', 0), ('-15', -15), ('55', 55), ))
def test_type_number(value: str, target: int):
    ret = NumberItem._state_from_oh_str(value)
    assert ret == target
    assert isinstance(ret, int)

    ret = map_openhab_values('Number', value)
    assert ret == target
    assert isinstance(ret, int)


@pytest.mark.parametrize(
    'value, target', (('0.0', 0.0), ('-99.99', -99.99), ('99.99', 99.99), ('0', 0), ('-15', -15), ('55', 55), )
)
def test_type_decimal(value: str, target: int):
    ret = NumberItem._state_from_oh_str(value)
    assert ret == target
    assert type(ret) is target.__class__

    ret = map_openhab_values('Decimal', value)
    assert ret == target
    assert type(ret) is target.__class__


@pytest.mark.parametrize(
    'value, target', (
        pytest.param('2023-06-17T15:31:04.754673068+0200', datetime(2023, 6, 17, 15, 31, 4, 754673), id='T1'),
        pytest.param('2023-06-17T15:31:04.754673+0200',    datetime(2023, 6, 17, 15, 31, 4, 754673), id='T2'),
        pytest.param('2023-06-17T15:31:04.754+0200',       datetime(2023, 6, 17, 15, 31, 4, 754000), id='T3'),
    )
)
def test_type_datetime(value: str, target: datetime):
    assert DatetimeItem._state_from_oh_str(value) == target
    assert map_openhab_values('DateTime', value) == target


def test_quantity():
    q = map_openhab_values('Quantity', '0.0 °C')
    assert q.value == 0.0
    assert q.unit == '°C'

    q = map_openhab_values('Quantity', '22 W/m²')
    assert q.value == 22
    assert q.unit == 'W/m²'
