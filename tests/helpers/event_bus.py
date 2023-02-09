from typing import Any

import pytest

from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.internals import EventFilterBase, EventBusListener, EventBus, wrap_func


class TestEventBus(EventBus):
    __test__ = False  # prevents this class from being collected by pytest

    def __init__(self):
        super().__init__()
        self.allow_errors = False
        self.errors = []

    def listen_events(self, name: str, cb, filter: EventFilterBase):
        listener = EventBusListener(name, wrap_func(cb, name=f'TestFunc for {name}'), filter)
        self.add_listener(listener)

    def post_event(self, topic: str, event: Any):
        if not self.allow_errors:
            if topic == TOPIC_ERRORS or isinstance(event, HABAppException):
                self.errors.append(event)
        super().post_event(topic, event)


@pytest.yield_fixture(scope='function')
def eb():
    eb = TestEventBus()
    yield eb
    eb.remove_all_listeners()

    for event in eb.errors:
        if isinstance(event, HABAppException):
            for line in event.to_str().splitlines():
                print(line)
        else:
            print(event)

    assert not eb.errors
