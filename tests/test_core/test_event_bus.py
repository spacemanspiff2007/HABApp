from unittest.mock import MagicMock

from HABApp.core.events import ComplexEventValue, ValueChangeEvent, ValueUpdateEvent
from HABApp.core.events.filter import EventFilter, NoEventFilter, OrFilterGroup
from HABApp.core.internals import EventBus, EventBusListener, wrap_func


class TestEvent:
    pass


def test_repr(sync_worker) -> None:
    f = wrap_func(lambda x: x)

    listener = EventBusListener('test_name', f, NoEventFilter())
    assert listener.describe() == '"test_name" (filter=NoEventFilter())'

    listener = EventBusListener('test_name', f, EventFilter(ValueUpdateEvent, value='test1'))
    assert listener.describe() == '"test_name" (filter=EventFilter(type=ValueUpdateEvent, value=test1))'


def test_str_event(sync_worker) -> None:
    """Test simple event and add/remove"""
    event_history1 = []
    event_history2 = []
    eb = EventBus()

    def append_event(event) -> None:
        event_history1.append(event)
    func1 = wrap_func(append_event)

    def append_event2(event) -> None:
        event_history2.append(event)
    func2 = wrap_func(append_event2)

    listener1 = EventBusListener('str_test', func1, NoEventFilter())
    eb.add_listener(listener1)
    listener2 = EventBusListener('str_test', func2, NoEventFilter())
    eb.add_listener(listener2)

    eb.post_event('str_test', 'str_event')
    assert event_history1 == ['str_event']
    assert event_history2 == ['str_event']

    eb.remove_listener(listener1)
    eb.post_event('str_test', 'str_event_2')
    assert event_history1 == ['str_event']
    assert event_history2 == ['str_event', 'str_event_2']


def test_multiple_events(sync_worker) -> None:
    event_history = []
    eb = EventBus()
    target = ['str_event', TestEvent(), 'str_event2']

    def append_event(event) -> None:
        event_history.append(event)

    listener = EventBusListener(
        'test', wrap_func(append_event),
        OrFilterGroup(EventFilter(str), EventFilter(TestEvent)))
    eb.add_listener(listener)

    for k in target:
        eb.post_event('test', k)

    assert event_history == target


def test_complex_event_unpack(sync_worker) -> None:
    """Test that the ComplexEventValue get properly unpacked"""
    m = MagicMock()
    assert not m.called
    eb = EventBus()

    listener = EventBusListener('test_complex', wrap_func(m, name='test'), NoEventFilter())
    eb.add_listener(listener)

    eb.post_event('test_complex', ValueUpdateEvent('test_complex', ComplexEventValue('ValOld')))
    eb.post_event('test_complex',
                  ValueChangeEvent('test_complex', ComplexEventValue('ValNew'), ComplexEventValue('ValOld')))

    # assert that we have been called with exactly one arg
    for k in m.call_args_list:
        assert len(k[0]) == 1

    arg0 = m.call_args_list[0][0][0]
    arg1 = m.call_args_list[1][0][0]

    # Events for first post_value
    assert vars(arg0) == vars(ValueUpdateEvent('test_complex', 'ValOld'))
    assert vars(arg1) == vars(ValueChangeEvent('test_complex', 'ValNew', 'ValOld'))
