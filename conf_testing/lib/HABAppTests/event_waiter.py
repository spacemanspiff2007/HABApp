import logging
import time
from typing import Union

import HABApp
from HABApp.core.items import BaseValueItem
from HABApp.openhab.events import OpenhabEvent
from .compare_values import get_equal_text, get_bytes_text
from HABAppTests.errors import TestCaseFailed

log = logging.getLogger('HABApp.Tests')


class EventWaiter:
    def __init__(self, name: Union[BaseValueItem, str], event_type, timeout=1, check_value=True):
        if isinstance(name, BaseValueItem):
            name = name.name
        assert isinstance(name, str)

        self.event_name = name
        self.event_type = event_type
        self.event_listener = HABApp.core.EventBusListener(
            self.event_name,
            HABApp.core.WrappedFunction(self.__process_event),
            self.event_type
        )
        self.timeout = timeout
        self.check_value = check_value

        self._event = None
        self.last_event = None

    def __process_event(self, event):
        assert isinstance(event, self.event_type)
        self._event = event

    def wait_for_event(self, value=None) -> OpenhabEvent:

        start = time.time()
        self._event = None

        while self._event is None:
            time.sleep(0.01)

            if time.time() > start + self.timeout:
                raise TestCaseFailed(f'Timeout while waiting for ({str(self.event_type).split(".")[-1][:-2]}) '
                                     f'for {self.event_name} with value {get_bytes_text(value)}')

            if self._event is None:
                continue

            self.last_event = self._event
            if self.check_value:
                self.compare_event_value(value)

            self._event = None
            return self.last_event

        raise ValueError()

    def __enter__(self) -> 'EventWaiter':
        HABApp.core.EventBus.add_listener(self.event_listener)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        HABApp.core.EventBus.remove_listener(self.event_listener)

    def compare_event_value(self, value_set):
        value_get = self._event.value

        equal = value_get == value_set
        msg = f'Got event for {self._event.name}: {get_equal_text(value_set, value_get)}'

        if not equal:
            raise TestCaseFailed(msg)

        log.debug(msg)
        return equal
