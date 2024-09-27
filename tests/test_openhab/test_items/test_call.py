from immutables import Map

from HABApp.openhab.items import CallItem
from HABApp.openhab.map_items import map_item


def test_call_set_value() -> None:

    call = CallItem('my_call_item')
    call.set_value('03018,2722720')
    assert call.value == ('03018', '2722720')

    call = CallItem('my_call_item')
    call.set_value(('a', 'b'))
    assert call.value == ('a', 'b')


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
