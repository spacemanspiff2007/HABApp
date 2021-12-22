from typing import Any

import HABApp
from HABApp.core.const import MISSING
from . import ValueChangeEvent, ValueUpdateEvent


class EventFilter:
    def __init__(self, event_type, **kwargs):
        assert len(kwargs) < 3, 'EventFilter only allows up to two args that will be used to filter'

        for arg in kwargs:
            if arg not in event_type.__annotations__:
                raise AttributeError(f'Filter attribute "{arg}" does not exist for "{event_type.__name__}"')

        self.__cls = event_type
        self.__filter = kwargs

    def create_event_listener(self, name, cb) -> 'HABApp.core.EventBusListener':
        kwargs = {'event_type': self.__cls}
        ct = 1
        for k, v in self.__filter.items():
            kwargs[f'attr_name{ct}'] = k
            kwargs[f'attr_value{ct}'] = v
            ct += 1

        return HABApp.core.EventBusListener(name, cb, **kwargs)

    def __repr__(self):
        name = self.__class__.__name__
        vals = [f'{k}={v}' for k, v in self.__filter.items()]
        if name == EventFilter.__name__:
            vals.insert(0, f'event_type={self.__cls.__name__}')
        return f'{name}({", ".join(vals)})'


class ValueUpdateEventFilter(EventFilter):
    _EVENT_TYPE = ValueUpdateEvent

    def __init__(self, value):
        super().__init__(self._EVENT_TYPE, value=value)


class ValueChangeEventFilter(EventFilter):
    _EVENT_TYPE = ValueChangeEvent

    def __init__(self, value: Any = MISSING, old_value: Any = MISSING):
        args = {}
        if value is not MISSING:
            args['value'] = value
        if old_value is not MISSING:
            args['old_value'] = old_value
        super().__init__(self._EVENT_TYPE, **args)
