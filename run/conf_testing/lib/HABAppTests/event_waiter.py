import asyncio
import logging
import time
from collections.abc import Generator
from time import monotonic
from types import TracebackType
from typing import Any

from HABApp.core.events.filter import EventFilter
from HABApp.core.internals import (
    EventBusListener,
    EventFilterBase,
    get_current_context,
    wrap_func,
)
from HABApp.core.items import BaseValueItem
from HABAppTests.errors import TestCaseFailed

from .compare_values import get_equal_text, get_value_text


log = logging.getLogger('HABApp.Tests')


class EventWaiter:
    def __init__(self, name: BaseValueItem | str,
                 event_filter: EventFilterBase, timeout: float = 1) -> None:
        if isinstance(name, BaseValueItem):
            name = name.name
        assert isinstance(name, str)
        assert isinstance(event_filter, EventFilterBase)

        self._name = name
        self._event_filter = event_filter
        self._timeout = timeout

        self._event_listener = EventBusListener(
            self._name,
            wrap_func(self.__process_event),
            self._event_filter
        )

        self._received_events = []

    def __process_event(self, event) -> None:
        if isinstance(self._event_filter, EventFilter):
            assert isinstance(event, self._event_filter.event_class)
        self._received_events.append(event)

    def clear(self) -> None:
        self._received_events.clear()

    def _check_wait_event(self, attribs: dict[str, Any]) -> Generator[float, Any, Any]:
        start = monotonic()
        end = start + self._timeout

        while monotonic() < end:
            yield 0.01

            if not self._received_events:
                continue

            event = self._received_events.pop()

            if attribs:
                if self.compare_event_value(event, attribs):
                    return event
                continue

            return event

        expected_values = 'with ' + ', '.join([f'{__k}={__v}' for __k, __v in attribs.items()]) if attribs else ''
        msg = f'Timeout while waiting for {self._event_filter.describe()} for {self._name} {expected_values}'
        raise TestCaseFailed(msg)

    def wait_for_event(self, **kwargs: Any) -> Any:
        gen = self._check_wait_event(kwargs)
        try:
            while True:
                delay = next(gen)
                time.sleep(delay)
        except StopIteration as e:
            event = e.value

        if event is None:
            raise ValueError()
        return event

    async def async_wait_for_event(self, **kwargs: Any) -> Any:
        gen = self._check_wait_event(kwargs)
        try:
            while True:
                delay = next(gen)
                await asyncio.sleep(delay)
        except StopIteration as e:
            event = e.value

        if event is None:
            raise ValueError()
        return event

    def __enter__(self) -> 'EventWaiter':
        get_current_context().add_event_listener(self._event_listener)
        return self

    def __exit__(self, exc_type: type[BaseException] | None,
                 exc_val: BaseException | None, exc_tb: TracebackType | None) -> bool:
        get_current_context().remove_event_listener(self._event_listener)

    @staticmethod
    def compare_event_value(event: Any, kwargs: dict[str, Any]) -> bool:
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
