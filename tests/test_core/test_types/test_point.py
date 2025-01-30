import pytest

from HABApp.core.types.point import Point


def test_access() -> None:
    lat = 52.51870523376821
    long = 13.376072914752532
    elev = 10

    p = Point(lat, long, elev)

    assert p[0] == lat
    assert p['lat'] == lat
    assert p['latitude'] == lat

    assert p[1] == long
    assert p['long'] == long
    assert p['longitude'] == long

    assert p[2] == elev
    assert p['elev'] == elev
    assert p['elevation'] == elev

    a, b, c = p
    assert a == lat
    assert b == long
    assert c == elev

    assert tuple(p) == (p.latitude, p.longitude, p.elevation)

    assert str(p) == 'Point(52.51870523376821, 13.376072914752532, 10)'

    a = Point(1, 2)
    assert a == Point(1, 2)
    assert a != Point(1, 2, 0)
    assert a != Point(1, 2, 3)

    a = Point(1, 2, 3)
    assert a == Point(1, 2, 3)
    assert a != Point(1, 2)


def test_point_create() -> None:
    with pytest.raises(ValueError) as e:
        Point(400, 2, 3)
    assert str(e.value) == 'Latitude must be between -90 and 90'

    with pytest.raises(ValueError) as e:
        Point(1, 200, 3)
    assert str(e.value) == 'Longitude must be between -180 and 180'

    with pytest.raises(TypeError) as e:
        Point(1, 2, '')
    assert str(e.value) == 'Elevation must be int or float'
