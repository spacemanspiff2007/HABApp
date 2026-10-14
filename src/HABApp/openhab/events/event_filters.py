from typing import Any, Final, override

from HABApp.core.const import MISSING, MISSING_TYPE
from HABApp.core.events.filter.event import TypeBoundEventFilter
from HABApp.core.internals import EventFilterBase
from HABApp.openhab.events.item_events import (
    ItemCommandEvent,
    ItemStateChangedEvent,
    ItemStateEvent,
    ItemStateUpdatedEvent,
)


# TODO: Drop this when we go OH4.0 only
class ItemStateEventFilter(TypeBoundEventFilter):
    __slots__ = ()

    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ItemStateEvent, value=value)


class ItemStateUpdatedEventFilter(TypeBoundEventFilter):
    __slots__ = ()

    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ItemStateUpdatedEvent, value=value)


class ItemStateChangedEventFilter(TypeBoundEventFilter):
    __slots__ = ()

    def __init__(self, value: Any = MISSING, old_value: Any = MISSING) -> None:
        super().__init__(ItemStateChangedEvent, value=value, old_value=old_value)


class ItemCommandEventFilter(TypeBoundEventFilter):
    __slots__ = ()

    def __init__(self, value: Any = MISSING) -> None:
        super().__init__(ItemCommandEvent, value=value)


class EventSourceFilter(EventFilterBase):
    """Filters events based on the ``bundle`` and/or ``actor`` of the (origin of the) event source.

    Only events that have a ``source`` attribute (i.e. :class:`ItemStateUpdatedEvent`,
    :class:`ItemStateChangedEvent` and :class:`ItemCommandEvent`) are able to trigger. Events without a
    ``source`` attribute, or whose source is empty/``None``, will never trigger.

    """

    __slots__ = ('actor', 'bundle')

    def __init__(self, bundle: str | MISSING_TYPE = MISSING, actor: str | MISSING_TYPE = MISSING) -> None:
        if bundle is MISSING and actor is MISSING:
            msg = 'At least one of "bundle" or "actor" must be specified'
            raise ValueError(msg)

        self.bundle: Final = bundle
        self.actor: Final = actor

    @override
    def trigger(self, event: Any) -> bool:
        if not isinstance(event, (ItemStateUpdatedEvent, ItemStateChangedEvent, ItemCommandEvent)):
            return False

        source: Final = event.source
        if not source:
            return False

        if self.bundle is not MISSING and source.bundle != self.bundle:
            return False

        return not (self.actor is not MISSING and source.actor != self.actor)

    @override
    def describe(self) -> str:
        values = []
        if self.bundle is not MISSING:
            values.append(f'bundle={self.bundle}')
        if self.actor is not MISSING:
            values.append(f'actor={self.actor}')

        return f'{self.__class__.__name__}({", ".join(values)})'
