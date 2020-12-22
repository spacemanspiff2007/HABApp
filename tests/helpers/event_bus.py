
import pytest
import typing

from HABApp.core import EventBus, EventBusListener
from HABApp.core import WrappedFunction


class TmpEventBus:
    def __init__(self):
        self.listener: typing.List[EventBusListener] = []

    def listen_events(self, name: str, cb):
        listener = EventBusListener(name, WrappedFunction(cb, name=f'TestFunc for {name}'))
        self.listener.append(listener)
        EventBus.add_listener(listener)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for listener in self.listener:
            listener.cancel()
        return False  # do not suppress exception


@pytest.fixture(scope="function")
def event_bus():
    with TmpEventBus() as tb:
        yield tb
