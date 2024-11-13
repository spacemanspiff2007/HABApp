from typing import Any

from typing_extensions import override

from HABApp.core.internals import AutoContextBoundObj, EventFilterBase, uses_event_bus
from HABApp.core.internals.event_bus import EventBusBaseListener
from HABApp.core.internals.wrapped_function import WrappedFunctionBase


event_bus = uses_event_bus()


class EventBusListener(EventBusBaseListener):
    def __init__(self, topic: str, callback: WrappedFunctionBase, event_filter: EventFilterBase, **kwargs: Any) -> None:
        super().__init__(topic, **kwargs)

        assert isinstance(callback, WrappedFunctionBase)
        self.func: WrappedFunctionBase = callback
        self.filter: EventFilterBase = event_filter

    def notify_listeners(self, event: Any) -> None:
        if self.filter.trigger(event):
            self.func.run(event)

    def describe(self) -> str:
        return f'"{self.topic}" (filter={self.filter.describe()})'

    def cancel(self) -> None:
        """Stop listening on the event bus"""
        event_bus.remove_listener(self)


class ContextBoundEventBusListener(EventBusListener, AutoContextBoundObj):

    @override
    def _ctx_unlink(self):
        event_bus.remove_listener(self)
        return super()._ctx_unlink()

    @override
    def cancel(self) -> None:
        """Stop listening on the event bus"""
        self._ctx_unlink()
