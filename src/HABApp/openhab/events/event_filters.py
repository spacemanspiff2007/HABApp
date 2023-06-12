from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events.filter.event import TypeBoundEventFilter
from . import ItemStateChangedEvent, ItemStateUpdatedEvent, ItemCommandEvent


class ItemStateUpdatedEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING):
        super().__init__(ItemStateUpdatedEvent, value=value)


class ItemStateChangedEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING, old_value: Any = MISSING):
        super().__init__(ItemStateChangedEvent, value=value, old_value=old_value)


class ItemCommandEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING):
        super().__init__(ItemCommandEvent, value=value)
