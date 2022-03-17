from typing import Optional, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    import HABApp

from HABApp.core.internals.event_bus import EventBusBaseListener
from HABApp.core.internals.wrapped_function import TYPE_WRAPPED_FUNC_OBJ, WrappedFunctionBase
from HABApp.core.internals import uses_event_bus
from HABApp.core.internals import TYPE_EVENT_FILTER_OBJ


EventBus = uses_event_bus()


class EventBusListener(EventBusBaseListener):
    def __init__(self, topic: str, callback: TYPE_WRAPPED_FUNC_OBJ, event_filter: TYPE_EVENT_FILTER_OBJ):
        super().__init__(topic)
        assert isinstance(callback, WrappedFunctionBase)
        self.func: TYPE_WRAPPED_FUNC_OBJ = callback
        self.filter: TYPE_EVENT_FILTER_OBJ = event_filter

        # Optional rule context if the listener was created in a Rule
        self._habapp_rule_ctx: Optional['HABApp.rule_ctx.HABAppRuleContext'] = None

    def notify_listeners(self, event):
        if self.filter.trigger(event):
            self.func.run(event)

    def describe(self):
        return f'"{self.topic}" (filter={self.filter.describe()})'

    def cancel(self):
        """Stop listening on the event bus"""
        EventBus.remove_listener(self)

        # If we have a context remove the listener from there, too
        if self._habapp_rule_ctx is not None:
            self._habapp_rule_ctx.remove_event_listener(self)
            self._habapp_rule_ctx = None


TYPE_EVENT_BUS_LISTENER = TypeVar('TYPE_EVENT_BUS_LISTENER', bound=EventBusListener)
