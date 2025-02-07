from immutables import Map

from HABApp.core.types import Point
from HABApp.openhab.items import CallItem, LocationItem
from HABApp.openhab.map_items import map_item


def test_call_set_value() -> None:
    call = CallItem('my_call_item')
    call.set_value(('03,018', '2722720'))
    assert call.value == ('03,018', '2722720')

    call = CallItem('my_call_item')
    call.set_value(('a', 'b'))
    assert call.value == ('a', 'b')


def test_call_post_update(websocket_events) -> None:
    call = CallItem('my_call_item')

    call.oh_post_update(('asdf', ))
    websocket_events.assert_called_once('StringList', 'asdf', event='update')

    call.oh_post_update(('a', 'b'))
    websocket_events.assert_called_once('StringList', 'a,b', event='update')

    call.oh_post_update(['a', '0,1'])
    websocket_events.assert_called_once('StringList', r'a,0\,1', event='update')


def test_call_map() -> None:
    call = map_item(
        'my_call_item', 'Call', 'my_value', label='l', tags=frozenset(), groups=frozenset(), metadata=None,)
    assert isinstance(call, CallItem)
    assert call.value == ('my_value', )

    assert call.label == 'l'
    assert call.tags == frozenset()
    assert call.groups == frozenset()
    assert call.metadata == Map()

    i = map_item(
        'my_call_item', 'Call', '03018,2722720', label='l', tags=frozenset(), groups=frozenset(), metadata=None,)
    assert isinstance(i, CallItem)
    assert i.value == ('03018', '2722720')

    assert call.label == 'l'
    assert call.tags == frozenset()
    assert call.groups == frozenset()
    assert call.metadata == Map()


def test_location_set_value() -> None:
    call = LocationItem('my_location_item')
    call.set_value((-10, 20))
    assert call.value == Point(-10, 20, None)

    call = LocationItem('my_location_item')
    call.set_value((1, 2, 3.3))
    assert call.value == Point(1, 2, 3.3)


def test_location_post_update(websocket_events) -> None:
    call = LocationItem('my_call_item')

    call.oh_post_update((45, -60))
    websocket_events.assert_called_once('Point', '45,-60', event='update')

    call.oh_post_update((-30, 179, 78.901))
    websocket_events.assert_called_once('Point', '-30,179,78.901', event='update')


def test_location_map() -> None:
    call = map_item(
        'my_call_item', 'Location', '52.518705,13.376072', label='l',
        tags=frozenset(), groups=frozenset(), metadata=None,
    )
    assert isinstance(call, LocationItem)
    assert call.value == (52.518705, 13.376072, None)

    assert call.label == 'l'
    assert call.tags == frozenset()
    assert call.groups == frozenset()
    assert call.metadata == Map()

    i = map_item(
        'my_call_item', 'Location', '52.518705,13.376072,43', label='l',
        tags=frozenset(), groups=frozenset(), metadata=None,
    )
    assert isinstance(i, LocationItem)
    assert i.value == (52.518705, 13.376072, 43)

    assert call.label == 'l'
    assert call.tags == frozenset()
    assert call.groups == frozenset()
    assert call.metadata == Map()
