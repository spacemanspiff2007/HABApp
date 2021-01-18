from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events import EventFilter
from . import ItemStateChangedEvent, ItemStateEvent


class ItemStateEventFilter(EventFilter):
    def __init__(self, *, value):
        super().__init__(ItemStateEvent, value=value)


class ItemStateChangedEventFilter(EventFilter):
    def __init__(self, *, value: Any = MISSING, old_value: Any = MISSING):
        args = {}
        if value is not MISSING:
            args['value'] = value
        if old_value is not MISSING:
            args['old_value'] = old_value
        super().__init__(ItemStateChangedEvent, **args)
