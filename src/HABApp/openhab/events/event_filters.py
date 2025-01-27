from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events.filter.event import TypeBoundEventFilter
from HABApp.openhab.events.item_events import (
    ItemCommandEvent,
    ItemStateChangedEvent,
    ItemStateEvent,
    ItemStateUpdatedEvent,
)


# TODO: Drop this when we go OH4.0 only
class ItemStateEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ItemStateEvent, value=value)


class ItemStateUpdatedEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ItemStateUpdatedEvent, value=value)


class ItemStateChangedEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING, old_value: Any = MISSING) -> None:
        super().__init__(ItemStateChangedEvent, value=value, old_value=old_value)


class ItemCommandEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ItemCommandEvent, value=value)
