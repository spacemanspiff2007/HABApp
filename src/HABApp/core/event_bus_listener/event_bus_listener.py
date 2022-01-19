from HABApp.core import WrappedFunction
from HABApp.core.events.filter.base import TYPE_FILTER_OBJ
from .base import EventBusListenerBase


class EventBusListener(EventBusListenerBase):
    def __init__(self, topic, callback, event_filter: TYPE_FILTER_OBJ):
        super().__init__(topic)
        assert isinstance(callback, WrappedFunction)

        self.func: WrappedFunction = callback
        self.filter: TYPE_FILTER_OBJ = event_filter

    def notify_listeners(self, event):
        if self.filter.trigger(event):
            self.func.run(event)

    def describe(self):
        return f'"{self.topic}" (filter={self.filter.describe()})'
