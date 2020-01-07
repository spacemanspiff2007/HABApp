from datetime import datetime

from HABApp.openhab.map_values import map_openhab_values


def test_type_none():
    assert map_openhab_values('UnDef', '0') is None
    assert map_openhab_values('Number', 'NULL') is None


def test_type_number():
    assert 0 == map_openhab_values('Number', '0')
    assert -99 == map_openhab_values('Number', '-99')
    assert 99 == map_openhab_values('Number', '99')


def test_type_decimal():
    assert 0.0 == map_openhab_values('Decimal', '0.0')
    assert -99.99 == map_openhab_values('Decimal', '-99.99')
    assert 99.99 == map_openhab_values('Decimal', '99.99')
    assert 5 == map_openhab_values('Decimal', '5')


def test_type_datetime():
    # test now
    _now = datetime.now().replace(microsecond=456000)
    _in = _now.astimezone(None).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + _now.astimezone(None).strftime('%z')
    # 2019-10-09T07:37:00.000+0200
    assert map_openhab_values('DateTime', _in) == _now


def test_quantity():
    q = map_openhab_values('Quantity', '0.0 °C')
    assert q.value == 0.0
    assert q.unit == '°C'

    q = map_openhab_values('Quantity', '22 W/m²')
    assert q.value == 22
    assert q.unit == 'W/m²'
