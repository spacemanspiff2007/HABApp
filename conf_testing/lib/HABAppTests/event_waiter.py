import logging
import time
from typing import TypeVar, Type, Dict, Any
from typing import Union

import HABApp
from HABApp.core.items import BaseValueItem
from HABAppTests.errors import TestCaseFailed
from .compare_values import get_equal_text, get_value_text

log = logging.getLogger('HABApp.Tests')

EVENT_TYPE = TypeVar('EVENT_TYPE')


class EventWaiter:
    def __init__(self, name: Union[BaseValueItem, str], event_type: Type[EVENT_TYPE], timeout=1):
        if isinstance(name, BaseValueItem):
            name = name.name
        assert isinstance(name, str)

        self.name = name
        self.event_type = event_type
        self.timeout = timeout

        self.event_listener = HABApp.core.EventBusListener(
            self.name,
            HABApp.core.WrappedFunction(self.__process_event),
            self.event_type
        )

        self._received_events = []

    def __process_event(self, event):
        assert isinstance(event, self.event_type)
        self._received_events.append(event)

    def clear(self):
        self._received_events.clear()

    def wait_for_event(self, **kwargs) -> EVENT_TYPE:

        start = time.time()

        while True:
            time.sleep(0.02)

            if time.time() > start + self.timeout:
                expected_values = "with " + ", ".join([f"{__k}={__v}" for __k, __v in kwargs.items()]) if kwargs else ""
                raise TestCaseFailed(f'Timeout while waiting for ({str(self.event_type).split(".")[-1][:-2]}) '
                                     f'for {self.name} {expected_values}')

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
        HABApp.core.EventBus.add_listener(self.event_listener)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        HABApp.core.EventBus.remove_listener(self.event_listener)

    @staticmethod
    def compare_event_value(event, kwargs: Dict[str, Any]):
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
