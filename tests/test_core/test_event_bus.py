from unittest.mock import MagicMock

from pytest import fixture

from HABApp.core import EventBus, EventBusListener, wrappedfunction
from HABApp.core.events import ComplexEventValue, ValueChangeEvent, ValueUpdateEvent
from HABApp.core.events.filter import AllEventsFilter, EventFilter, OrFilterGroup
from HABApp.core.items import Item


class TestEvent:
    pass


@fixture
def clean_event_bus():
    EventBus.remove_all_listeners()
    yield EventBus
    EventBus.remove_all_listeners()


def test_repr(clean_event_bus: EventBus, sync_worker):
    f = wrappedfunction.WrappedFunction(lambda x: x)

    listener = EventBusListener('test_name', f, AllEventsFilter())
    assert listener.describe() == '"test_name" (filter=AllEventsFilter())'

    listener = EventBusListener('test_name', f, EventFilter(ValueUpdateEvent, value='test1'))
    assert listener.describe() == '"test_name" (filter=EventFilter(type=ValueUpdateEvent, value=test1))'


def test_str_event(clean_event_bus: EventBus, sync_worker):
    event_history = []

    def append_event(event):
        event_history.append(event)
    func = wrappedfunction.WrappedFunction(append_event)

    listener = EventBusListener('str_test', func, AllEventsFilter())
    EventBus.add_listener(listener)

    EventBus.post_event('str_test', 'str_event')
    assert event_history == ['str_event']


def test_multiple_events(clean_event_bus: EventBus, sync_worker):
    event_history = []
    target = ['str_event', TestEvent(), 'str_event2']

    def append_event(event):
        event_history.append(event)

    listener = EventBusListener(
        'test', wrappedfunction.WrappedFunction(append_event),
        OrFilterGroup(EventFilter(str), EventFilter(TestEvent)))
    EventBus.add_listener(listener)

    for k in target:
        EventBus.post_event('test', k)

    assert event_history == target


def test_complex_event_unpack(clean_event_bus: EventBus, sync_worker):
    """Test that the ComplexEventValue get properly unpacked"""
    m = MagicMock()
    assert not m.called

    item = Item.get_create_item('test_complex')
    listener = EventBusListener(item.name, wrappedfunction.WrappedFunction(m, name='test'), AllEventsFilter())
    EventBus.add_listener(listener)

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
