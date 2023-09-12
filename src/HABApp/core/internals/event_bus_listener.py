from typing import Optional, TypeVar

from HABApp.core.internals.event_bus import EventBusBaseListener
from HABApp.core.internals.wrapped_function import TYPE_WRAPPED_FUNC_OBJ, WrappedFunctionBase
from HABApp.core.internals import uses_event_bus, Context
from HABApp.core.internals import HINT_EVENT_FILTER_OBJ, AutoContextBoundObj


event_bus = uses_event_bus()


class EventBusListener(EventBusBaseListener):
    def __init__(self, topic: str, callback: TYPE_WRAPPED_FUNC_OBJ, event_filter: HINT_EVENT_FILTER_OBJ, **kwargs):
        super().__init__(topic, **kwargs)

        assert isinstance(callback, WrappedFunctionBase)
        self.func: TYPE_WRAPPED_FUNC_OBJ = callback
        self.filter: HINT_EVENT_FILTER_OBJ = event_filter

    def notify_listeners(self, event):
        if self.filter.trigger(event):
            self.func.run(event)

    def describe(self) -> str:
        return f'"{self.topic}" (filter={self.filter.describe()})'

    def cancel(self):
        """Stop listening on the event bus"""
        event_bus.remove_listener(self)


HINT_EVENT_BUS_LISTENER = TypeVar('HINT_EVENT_BUS_LISTENER', bound=EventBusListener)


class ContextBoundEventBusListener(EventBusListener, AutoContextBoundObj):
    def __init__(self, topic: str, callback: TYPE_WRAPPED_FUNC_OBJ, event_filter: HINT_EVENT_FILTER_OBJ,
                 parent_ctx: Optional[Context] = None):
        super().__init__(topic=topic, callback=callback, event_filter=event_filter, parent_ctx=parent_ctx)

        assert isinstance(callback, WrappedFunctionBase)
        self.func: TYPE_WRAPPED_FUNC_OBJ = callback
        self.filter: HINT_EVENT_FILTER_OBJ = event_filter

    def notify_listeners(self, event):
        if self.filter.trigger(event):
            self.func.run(event)

    def describe(self) -> str:
        return f'"{self.topic}" (filter={self.filter.describe()})'

    def _ctx_unlink(self):
        event_bus.remove_listener(self)
        return super()._ctx_unlink()

    def cancel(self):
        """Stop listening on the event bus"""
        self._ctx_unlink()
