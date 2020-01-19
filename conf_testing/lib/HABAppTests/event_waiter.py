import logging
import time

import HABApp
from .compare_values import get_equal_text

log = logging.getLogger('HABApp.Tests')


class EventWaiter:
    def __init__(self, name, event_type, timeout=1, check_value=True):
        self.event_name = name
        assert isinstance(name, str)
        self.event_type = event_type
        self.event_listener = HABApp.core.EventBusListener(
            self.event_name,
            HABApp.core.WrappedFunction(self.__process_event),
            self.event_type
        )
        self.timeout = timeout
        self.event = None
        self.check_value = check_value

        self.events_ok = True

    def __process_event(self, event):
        assert isinstance(event, self.event_type)
        self.event = event

    def wait_for_event(self, value=None):

        start = time.time()
        self.event = None
        while self.event is None:
            time.sleep(0.01)

            if time.time() > start + self.timeout:
                self.events_ok = False
                log.error(f'Timeout while waiting for ({str(self.event_type).split(".")[-1][:-2]}) '
                          f'for {self.event_name} with value {value}')
                return False

            if self.event is None:
                continue

            if self.check_value:
                values_same = self.compare_event_value(value)
                if not values_same:
                    self.events_ok = False

                self.event = None
                return values_same

            self.event = None
            return True

        raise ValueError()

    def __enter__(self) -> 'EventWaiter':
        HABApp.core.EventBus.add_listener(self.event_listener)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        HABApp.core.EventBus.remove_listener(self.event_listener)

    def compare_event_value(self, value_set):
        value_get = self.event.value

        equal = value_get == value_set

        (log.debug if equal else log.error)(f'Got event for {self.event.name}: '
                                            f'{get_equal_text(value_set, value_get)}')
        return equal
