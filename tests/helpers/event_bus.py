from collections.abc import Generator
from typing import Any

import pytest

from HABApp.core.const.topics import TOPIC_ERRORS
from HABApp.core.events.habapp_events import HABAppException
from HABApp.core.internals import EventBus, EventBusListener, EventFilterBase
from HABApp.core.internals.function_executor.factory import ExecutorFactory
from HABApp.core.provider import HABAPP_PROVIDER


class TestEventBus(EventBus):
    __test__ = False  # prevents this class from being collected by pytest

    def __init__(self) -> None:
        super().__init__()
        self.allow_errors = False
        self.errors = []
        self.worker_factory: ExecutorFactory | None = None

    def listen_events(self, name: str, cb, filter: EventFilterBase) -> None:
        assert self.worker_factory is not None
        func = self.worker_factory.create(cb, name=f'TestFunc for {name}')

        listener = EventBusListener(name, func, filter)
        self.add_listener(listener)

    def post_event(self, topic: str, event: Any) -> None:
        if not self.allow_errors:
            if topic == TOPIC_ERRORS or isinstance(event, HABAppException):
                self.errors.append(event)
        super().post_event(topic, event)


@pytest.fixture
def eb() -> Generator[TestEventBus, Any, None]:
    eb = TestEventBus()

    # ToDo: rework so we don't have to add it to HABAPP_PROVIDER
    HABAPP_PROVIDER.add_object(eb, EventBus)
    yield eb
    HABAPP_PROVIDER._created.pop(EventBus, None)

    eb.remove_all_listeners()

    for event in eb.errors:
        if isinstance(event, HABAppException):
            for line in event.to_str().splitlines():
                print(line)
        else:
            print(event)

    assert not eb.errors
