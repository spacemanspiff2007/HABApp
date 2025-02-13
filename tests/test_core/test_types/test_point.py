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

    assert a == (1, 2)
    assert a != (1, 2, 0)
    assert a != (1, 2, 3)

    a = Point(1, 2, 3)
    assert a == Point(1, 2, 3)
    assert a != Point(1, 2)

    assert a == (1, 2, 3)
    assert a != (1, 2)


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


def test_distance() -> None:
    # from https://geopy.readthedocs.io/en/latest/#module-geopy.distance
    a = Point(41.49008, -71.312796)
    b = Point(41.499498, -81.695391)
    d = 538.390_445
    assert round(a.distance(b, unit='miles'), 6) == d
    assert round(a.distance((41.499498, -81.695391), unit='miles'), 6) == d
    assert round(a.distance((41.499498, -81.695391, 99_999), unit='miles'), 6) == d

    a = Point(52.51870523376821, 13.376072914752532, 10)
    b = Point(52.986881, 10.109257)
    assert round(a.distance(b), 3) == 226.623
    assert round(a.distance(b, unit='m'), 0) == 226_623
