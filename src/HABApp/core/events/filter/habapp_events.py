from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.events.filter.event import TypeBoundEventFilter


class ValueUpdateEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ValueUpdateEvent, value=value)


class ValueChangeEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING, old_value: Any = MISSING) -> None:
        super().__init__(ValueChangeEvent, value=value, old_value=old_value)
