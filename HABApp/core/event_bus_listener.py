import HABApp
from . import WrappedFunction
from .events import AllEvents


class EventBusListener:
    def __init__(self, topic, callback, event_type=AllEvents):
        assert isinstance(topic, str) or topic is None, type(topic)
        assert isinstance(callback, WrappedFunction)

        self.topic: str = topic
        self.func: WrappedFunction = callback

        self.event_filter = event_type

    def notify_listeners(self, event):

        if self.event_filter is AllEvents or isinstance(event, self.event_filter):
            self.func.run(event)
            return None

        # Make it possible to specify multiple classes
        if isinstance(self.event_filter, list) or isinstance(self.event_filter, set):
            for cls in self.event_filter:
                if isinstance(event, cls):
                    self.func.run(event)
                    return None

    def cancel(self):
        """Stop listening on the event bus"""
        HABApp.core.EventBus.remove_listener(self)
