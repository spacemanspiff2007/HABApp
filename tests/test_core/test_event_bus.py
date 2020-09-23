from pytest import fixture
from unittest.mock import MagicMock

from HABApp.core import EventBus, EventBusListener, wrappedfunction
from HABApp.core.items import Item
from HABApp.core.events import ComplexEventValue, ValueChangeEvent, ValueUpdateEvent
from ..helpers import SyncWorker


class TestEvent():
    pass


@fixture
def event_bus():
    EventBus.remove_all_listeners()
    yield EventBus
    EventBus.remove_all_listeners()


def test_str_event(event_bus: EventBus):
    event_history = []

    def set(event):
        event_history.append(event)

    listener = EventBusListener('str_test', wrappedfunction.WrappedFunction(set))
    EventBus.add_listener(listener)

    with SyncWorker():
        EventBus.post_event('str_test', 'str_event')

    assert event_history == ['str_event']


def test_multiple_events(event_bus: EventBus):
    event_history = []
    target = ['str_event', TestEvent(), 'str_event2']

    def set(event):
        event_history.append(event)

    listener = EventBusListener('test', wrappedfunction.WrappedFunction(set), (str, TestEvent))
    EventBus.add_listener(listener)

    with SyncWorker():
        for k in target:
            EventBus.post_event('test', k)

    assert event_history == target


def test_complex_event_unpack(event_bus: EventBus):
    """Test that the ComplexEventValue get properly unpacked"""
    m = MagicMock()
    assert not m.called

    item = Item.get_create_item('test_complex')
    listener = EventBusListener(item.name, wrappedfunction.WrappedFunction(m, name='test'))
    EventBus.add_listener(listener)

    with SyncWorker():
        item.post_value(ComplexEventValue('ValOld'))
        item.post_value(ComplexEventValue('ValNew'))

    # assert that we have been called with exactly one arg
    for k in m.call_args_list:
        assert len(k[0]) == 1

    arg0 = m.call_args_list[0][0][0]
    arg1 = m.call_args_list[1][0][0]
    arg2 = m.call_args_list[2][0][0]
    arg3 = m.call_args_list[3][0][0]

    # Events for first post_value
    assert vars(arg0) == vars(ValueUpdateEvent(item.name, 'ValOld'))
    assert vars(arg1) == vars(ValueChangeEvent(item.name, 'ValOld', None))

    # Events for second post_value
    assert vars(arg2) == vars(ValueUpdateEvent(item.name, 'ValNew'))
    assert vars(arg3) == vars(ValueChangeEvent(item.name, 'ValNew', 'ValOld'))
