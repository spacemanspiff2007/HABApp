from immutables import Map

from HABApp.openhab.items import CallItem, LocationItem
from HABApp.openhab.map_items import map_item


def test_call_set_value() -> None:
    call = CallItem('my_call_item')
    call.set_value('03018,2722720')
    assert call.value == ('03018', '2722720')

    call = CallItem('my_call_item')
    call.set_value(('a', 'b'))
    assert call.value == ('a', 'b')


def test_call_post_update(posted_updates):
    call = CallItem('my_call_item')

    call.oh_post_update('asdf')
    posted_updates.assert_called_with('asdf')

    call.oh_post_update(('a', 'b'))
    posted_updates.assert_called_with('a,b')

    call.oh_post_update(['a', '0'])
    posted_updates.assert_called_with('a,0')


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
    call.set_value('103018,2722720')
    assert call.value == (103018, 2722720, None)

    call = LocationItem('my_location_item')
    call.set_value((1, 2, 3.3))
    assert call.value == (1, 2, 3.3)


def test_location_post_update(posted_updates):
    call = LocationItem('my_call_item')

    call.oh_post_update((132, 456))
    posted_updates.assert_called_with('132,456')

    call.oh_post_update((132, 456, 78.901))
    posted_updates.assert_called_with('132,456,78.901')


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
