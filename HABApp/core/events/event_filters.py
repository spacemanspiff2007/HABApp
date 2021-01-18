from typing import Any

from HABApp.core.const import MISSING
from . import ValueChangeEvent, ValueUpdateEvent


class EventFilter:
    def __init__(self, cls, **kwargs):
        assert len(kwargs) < 3, 'Filter allows up to two args'

        for arg in kwargs:
            if arg not in cls.__annotations__:
                raise AttributeError(f'Filter attribute "{arg}" does not exist for "{cls.__name__}"')

        self.__cls = cls
        self.__filter = kwargs

    def get_args(self):
        ret = {'event_type': self.__cls}
        ct = 1
        for name, value in self.__filter.items():
            ret[f'prop_name{ct}'] = name
            ret[f'prop_value{ct}'] = value
            ct += 1
        return ret

    def __repr__(self):
        name = self.__class__.__name__
        vals = [f'{k}={v}' for k, v in self.__filter.items()]
        if name == EventFilter.__name__:
            vals.insert(0, f'event_type={self.__cls.__name__}')
        return f'{name}({", ".join(vals)})'


class ValueUpdateEventFilter(EventFilter):
    def __init__(self, *, value):
        super().__init__(ValueUpdateEvent, value=value)


class ValueChangeEventFilter(EventFilter):
    def __init__(self, *, value: Any = MISSING, old_value: Any = MISSING):
        args = {}
        if value is not MISSING:
            args['value'] = value
        if old_value is not MISSING:
            args['old_value'] = old_value
        super().__init__(ValueChangeEvent, **args)
