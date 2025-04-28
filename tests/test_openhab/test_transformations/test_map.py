import pytest
from immutables import Map

from HABApp.openhab.errors import MapTransformationError

# noinspection PyProtectedMember
from HABApp.openhab.transformations._map import MapTransformation, MapTransformationWithDefault

# noinspection PyProtectedMember
from HABApp.openhab.transformations._map.registry import MapTransformationRegistry


def test_classes() -> None:
    a = MapTransformation({1: 2}, name='myname')
    assert str(a) == '<MapTransformation name=myname items={1: 2}>'
    assert a[1] == 2
    with pytest.raises(KeyError):
        _ = a[5]

    a = MapTransformationWithDefault({1: 2}, name='myname', default='asdf')
    assert str(a) == '<MapTransformationWithDefault name=myname items={1: 2}, default=asdf>'
    assert a[1] == 2
    assert a[5] == 'asdf'

    with pytest.raises(MapTransformationError) as e:
        a.get(5)
    assert str(e.value) == 'Mapping is already defined with a default: "asdf"'


def test_parse_file_default() -> None:
    file = '''
ON=1
OFF=0
white\\ space=using escape
=default
'''

    m = MapTransformationRegistry('map')
    m.set('testobj', {'function': file})
    assert m.objs['testobj'] == (Map({'OFF': '0', 'ON': '1', 'white space': 'using escape'}), 'default')


def test_parse_file_int() -> None:
    file = '''
ON=1
OFF=0
=2
'''

    m = MapTransformationRegistry('map')
    m.set('testobj', {'function': file})
    assert m.objs['testobj'] == (Map({'OFF': 0, 'ON': 1}), 2)


def test_parse_file_int_keys() -> None:
    file = '''
1=asdf
2=qwer
'''
    m = MapTransformationRegistry('map')
    m.set('testobj', {'function': file})
    assert m.objs['testobj'] == (Map({1: 'asdf', 2: 'qwer'}), None)


def test_parse_file_int_values() -> None:
    file = '''
1=6
2=7
'''
    m = MapTransformationRegistry('map')
    m.set('testobj', {'function': file})
    assert m.objs['testobj'] == (Map({1: 6, 2: 7}), None)
