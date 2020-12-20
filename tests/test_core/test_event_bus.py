from unittest.mock import MagicMock

from pytest import fixture

from HABApp.core import EventBus, EventBusListener, wrappedfunction
from HABApp.core.events import ComplexEventValue, ValueChangeEvent, ValueUpdateEvent
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

    listener = EventBusListener('test_name', f)
    assert listener.desc() == '"test_name" (type AllEvents)'

    listener = EventBusListener('test_name', f, prop_name1='test1', prop_value1='value1')
    assert listener.desc() == '"test_name" (type AllEvents, test1==value1)'

    listener = EventBusListener('test_name', f, prop_name2='test2', prop_value2='value2')
    assert listener.desc() == '"test_name" (type AllEvents, test2==value2)'

    listener = EventBusListener('test_name', f, prop_name1='test1', prop_value1='value1',
                                prop_name2='test2', prop_value2='value2')
    assert listener.desc() == '"test_name" (type AllEvents, test1==value1, test2==value2)'


def test_str_event(clean_event_bus: EventBus, sync_worker):
    event_history = []

    def append_event(event):
        event_history.append(event)
    func = wrappedfunction.WrappedFunction(append_event)

    listener = EventBusListener('str_test', func)
    EventBus.add_listener(listener)

    EventBus.post_event('str_test', 'str_event')
    assert event_history == ['str_event']


def test_multiple_events(clean_event_bus: EventBus, sync_worker):
    event_history = []
    target = ['str_event', TestEvent(), 'str_event2']

    def append_event(event):
        event_history.append(event)

    listener = EventBusListener('test', wrappedfunction.WrappedFunction(append_event), (str, TestEvent))
    EventBus.add_listener(listener)

    for k in target:
        EventBus.post_event('test', k)

    assert event_history == target


def test_complex_event_unpack(clean_event_bus: EventBus, sync_worker):
    """Test that the ComplexEventValue get properly unpacked"""
    m = MagicMock()
    assert not m.called

    item = Item.get_create_item('test_complex')
    listener = EventBusListener(item.name, wrappedfunction.WrappedFunction(m, name='test'))
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


def test_event_filter_single(clean_event_bus: EventBus, sync_worker):
    events_all, events_filtered1, events_filtered2 = [], [], []

    def append_all(event):
        events_all.append(event)

    def append_filter1(event):
        events_filtered1.append(event)

    def append_filter2(event):
        events_filtered2.append(event)

    name = 'test_filter'
    func1 = wrappedfunction.WrappedFunction(append_filter1)
    func2 = wrappedfunction.WrappedFunction(append_filter2)

    # listener to all events
    EventBus.add_listener(
        EventBusListener(name, wrappedfunction.WrappedFunction(append_all))
    )

    listener = EventBusListener(name, func1, ValueUpdateEvent, 'value', 'test_value')
    EventBus.add_listener(listener)
    listener = EventBusListener(name, func2, ValueUpdateEvent, None, None, 'value', 1)
    EventBus.add_listener(listener)

    event0 = ValueUpdateEvent(name, None)
    event1 = ValueUpdateEvent(name, 'test_value')
    event2 = ValueUpdateEvent(name, 1)

    EventBus.post_event(name, event0)
    EventBus.post_event(name, event1)
    EventBus.post_event(name, event2)

    assert len(events_all) == 3
    assert vars(events_all[0]) == vars(event0)
    assert vars(events_all[1]) == vars(event1)
    assert vars(events_all[2]) == vars(event2)

    assert len(events_filtered1) == 1
    assert vars(events_filtered1[0]) == vars(event1)

    assert len(events_filtered2) == 1
    assert vars(events_filtered2[0]) == vars(event2)
