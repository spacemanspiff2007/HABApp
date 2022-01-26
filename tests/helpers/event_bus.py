
import pytest

from HABApp.core import WrappedFunction
from HABApp.core.base import EventFilterBase
from HABApp.core.impl import EventBusListener, EventBus


class TestEventBus(EventBus):
    def listen_events(self, name: str, cb, filter: EventFilterBase):
        listener = EventBusListener(name, WrappedFunction(cb, name=f'TestFunc for {name}'), filter)
        self.add_listener(listener)


@pytest.yield_fixture(scope='function')
def eb():
    eb = TestEventBus()
    yield eb
    eb.remove_all_listeners()
