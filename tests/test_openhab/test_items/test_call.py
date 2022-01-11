from HABApp.openhab.items import CallItem
from HABApp.openhab.map_items import map_item


def test_call_set_value():

    call = CallItem('my_call_item')
    call.set_value('03018,2722720')
    assert call.value == ('03018', '2722720')

    call = CallItem('my_call_item')
    call.set_value(('a', 'b'))
    assert call.value == ('a', 'b')


def test_call_map():
    call = map_item('my_call_item', 'Call', 'my_value', tags=frozenset(), groups=frozenset(), metadata=None,)
    assert isinstance(call, CallItem)
    assert call.value == ('my_value', )

    i = map_item('my_call_item', 'Call', '03018,2722720', tags=frozenset(), groups=frozenset(), metadata=None,)
    assert isinstance(i, CallItem)
    assert i.value == ('03018', '2722720')
