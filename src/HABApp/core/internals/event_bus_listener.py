from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, override

from HABApp.core.internals import AutoContextBoundObj
from HABApp.core.internals.event_bus import EventBusListenerBase


if TYPE_CHECKING:
    from HABApp.core.internals import EventFilterBase, FunctionExecutorBase


class EventBusListener(EventBusListenerBase):
    def __init__(self, topic: str, func: FunctionExecutorBase, event_filter: EventFilterBase, **kwargs: Any) -> None:
        super().__init__(topic, **kwargs)

        self._func: Final = func
        self._filter: Final = event_filter

    def notify_listeners(self, event: Any) -> None:
        if self._filter.trigger(event):
            self._func.execute_background(event)

    def describe(self) -> str:
        return f'"{self.topic}" (filter={self._filter.describe()})'

    def cancel(self) -> None:
        """Stop listening on the event bus"""
        if self._event_bus is not None:
            self._event_bus.remove_listener(self)


class ContextBoundEventBusListener(EventBusListener, AutoContextBoundObj):

    @override
    def _ctx_unlink(self) -> None:
        super()._ctx_unlink()
        # Then remove from event bus
        EventBusListener.cancel(self)

    @override
    def cancel(self) -> None:
        """Stop listening on the event bus"""
        self._ctx_unlink()
