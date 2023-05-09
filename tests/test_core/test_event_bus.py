from unittest.mock import MagicMock

from HABApp.core.events import ComplexEventValue, ValueChangeEvent, ValueUpdateEvent
from HABApp.core.events.filter import NoEventFilter, EventFilter, OrFilterGroup
from HABApp.core.internals import EventBus, EventBusListener, wrap_func
from HABApp.core.const.topics import TOPIC_ANY


class TestEvent:
    pass


def test_repr(sync_worker):
    f = wrap_func(lambda x: x)

    listener = EventBusListener('test_name', f, NoEventFilter())
    assert listener.describe() == '"test_name" (filter=NoEventFilter())'

    listener = EventBusListener('test_name', f, EventFilter(ValueUpdateEvent, value='test1'))
    assert listener.describe() == '"test_name" (filter=EventFilter(type=ValueUpdateEvent, value=test1))'


def test_str_event(sync_worker):
    event_history = []
    eb = EventBus()

    def append_event(event):
        event_history.append(event)
    func = wrap_func(append_event)

    listener = EventBusListener('str_test', func, NoEventFilter())
    eb.add_listener(listener)

    eb.post_event('str_test', 'str_event')
    assert event_history == ['str_event']


def test_catch_all_events(sync_worker):
    event_history_all = []
    event_history_selected = []
    eb = EventBus()

    def append_event_selected(event):
        event_history_selected.append(event)

    def append_event_all(event):
        event_history_all.append(event)

    listener = EventBusListener('topicA', wrap_func(append_event_selected), NoEventFilter())
    eb.add_listener(listener)
    listener_all = EventBusListener(TOPIC_ANY, wrap_func(append_event_all), NoEventFilter())
    eb.add_listener(listener_all)

    eb.post_event('topicA', 'valueA')
    eb.post_event('topicB', 'valueB')
    eb.post_event('topicC', 'valueC')
    assert event_history_selected == ['valueA']
    assert len(event_history_all) == 3




def test_multiple_events(sync_worker):
    event_history = []
    eb = EventBus()
    target = ['str_event', TestEvent(), 'str_event2']

    def append_event(event):
        event_history.append(event)

    listener = EventBusListener(
        'test', wrap_func(append_event),
        OrFilterGroup(EventFilter(str), EventFilter(TestEvent)))
    eb.add_listener(listener)

    for k in target:
        eb.post_event('test', k)

    assert event_history == target


def test_complex_event_unpack(sync_worker):
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
