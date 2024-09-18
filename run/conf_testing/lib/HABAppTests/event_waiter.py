import logging
import time
from typing import Any, TypeVar

from HABApp.core.events.filter import EventFilter
from HABApp.core.internals import (
    HINT_EVENT_FILTER_OBJ,
    EventBusListener,
    EventFilterBase,
    get_current_context,
    wrap_func,
)
from HABApp.core.items import BaseValueItem
from HABAppTests.errors import TestCaseFailed

from .compare_values import get_equal_text, get_value_text


log = logging.getLogger('HABApp.Tests')

EVENT_TYPE = TypeVar('EVENT_TYPE')


class EventWaiter:
    def __init__(self, name: BaseValueItem | str,
                 event_filter: HINT_EVENT_FILTER_OBJ, timeout=1):
        if isinstance(name, BaseValueItem):
            name = name.name
        assert isinstance(name, str)
        assert isinstance(event_filter, EventFilterBase)

        self.name = name
        self.event_filter = event_filter
        self.timeout = timeout

        self.event_listener = EventBusListener(
            self.name,
            wrap_func(self.__process_event),
            self.event_filter
        )

        self._received_events = []

    def __process_event(self, event):
        if isinstance(self.event_filter, EventFilter):
            assert isinstance(event, self.event_filter.event_class)
        self._received_events.append(event)

    def clear(self):
        self._received_events.clear()

    def wait_for_event(self, **kwargs) -> EVENT_TYPE:

        start = time.time()

        while True:
            time.sleep(0.02)

            if time.time() > start + self.timeout:
                expected_values = 'with ' + ', '.join([f'{__k}={__v}' for __k, __v in kwargs.items()]) if kwargs else ''
                msg = f'Timeout while waiting for {self.event_filter.describe()} for {self.name} {expected_values}'
                raise TestCaseFailed(msg)

            if not self._received_events:
                continue

            event = self._received_events.pop()

            if kwargs:
                if self.compare_event_value(event, kwargs):
                    return event
                continue

            return event

        raise ValueError()

    def __enter__(self) -> 'EventWaiter':
        get_current_context().add_event_listener(self.event_listener)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        get_current_context().remove_event_listener(self.event_listener)

    @staticmethod
    def compare_event_value(event, kwargs: dict[str, Any]):
        only_value = 'value' in kwargs and len(kwargs) == 1
        val_msg = []

        equal = True
        for key, expected in kwargs.items():
            value = getattr(event, key)
            if expected != value:
                equal = False
                val_msg.append((f'{key}: ' if not only_value else '') + get_equal_text(expected, value))
            else:
                val_msg.append((f'{key}: ' if not only_value else '') + get_value_text(value))

        log.debug(f'Got {event.__class__.__name__} for {event.name}: {", ".join(val_msg)}')
        return equal
