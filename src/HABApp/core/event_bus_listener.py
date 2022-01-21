import HABApp
from HABApp.core.base import TYPE_FILTER_OBJ, EventBusListenerBase, TYPE_WRAPPED_FUNC_OBJ, WrappedFunctionBase


class EventBusListener(EventBusListenerBase):
    def __init__(self, topic: str, callback: TYPE_WRAPPED_FUNC_OBJ, event_filter: TYPE_FILTER_OBJ):
        super().__init__(topic)
        assert isinstance(callback, WrappedFunctionBase)

        self.func: TYPE_WRAPPED_FUNC_OBJ = callback
        self.filter: TYPE_FILTER_OBJ = event_filter

    def notify_listeners(self, event):
        if self.filter.trigger(event):
            self.func.run(event)

    def describe(self):
        return f'"{self.topic}" (filter={self.filter.describe()})'

    def cancel(self):
        """Stop listening on the event bus"""
        HABApp.core.EventBus.remove_listener(self)

        # If we have a context remove the listener from there, too
        if self._habapp_rule_ctx is not None:
            self._habapp_rule_ctx.remove_event_listener(self)
            self._habapp_rule_ctx = None
