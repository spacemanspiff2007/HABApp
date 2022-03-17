import pytest

from HABApp.core.internals import EventFilterBase, EventBusListener, EventBus, wrap_func


class TestEventBus(EventBus):
    def listen_events(self, name: str, cb, filter: EventFilterBase):
        listener = EventBusListener(name, wrap_func(cb, name=f'TestFunc for {name}'), filter)
        self.add_listener(listener)


@pytest.yield_fixture(scope='function')
def eb():
    eb = TestEventBus()
    yield eb
    eb.remove_all_listeners()
