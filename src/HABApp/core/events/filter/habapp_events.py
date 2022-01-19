from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events import ValueUpdateEvent, ValueChangeEvent
from HABApp.core.events.filter.event import TypeBoundEventFilter
from HABApp.core.const.hints import ANY_CLASS


class ValueUpdateEventFilter(TypeBoundEventFilter):
    _EVENT_TYPE: ANY_CLASS = ValueUpdateEvent

    def __init__(self, value: Any = MISSING):
        args = {}
        if value is not MISSING:
            args['value'] = value
        super().__init__(self._EVENT_TYPE, **args)


class ValueChangeEventFilter(TypeBoundEventFilter):
    _EVENT_TYPE: ANY_CLASS = ValueChangeEvent

    def __init__(self, value: Any = MISSING, old_value: Any = MISSING):
        args = {}
        if value is not MISSING:
            args['value'] = value
        if old_value is not MISSING:
            args['old_value'] = old_value
        super().__init__(self._EVENT_TYPE, **args)
