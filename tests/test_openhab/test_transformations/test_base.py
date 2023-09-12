# noinspection PyProtectedMember
from HABApp.openhab.transformations._map.registry import MapTransformationRegistry


def test_sort():
    m = MapTransformationRegistry(name='map')
    m.objs['test.map'] = ({}, None)
    m.objs['aa.map'] = ({}, None)

    # UI generated transformation
    m.objs['config:map:test:map'] = ({}, None)

    assert m.available() == ('aa.map', 'test.map', 'config:map:test:map')
