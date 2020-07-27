from pytest import fixture

from HABApp.core import EventBus, EventBusListener, wrappedfunction
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
