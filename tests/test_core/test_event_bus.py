from HABApp.core.events import ValueUpdateEvent
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
