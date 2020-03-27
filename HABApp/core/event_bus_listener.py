import HABApp
from HABApp.core.events import AllEvents
from . import WrappedFunction


class EventBusListener:
    def __init__(self, topic, callback, event_type=AllEvents):
        assert isinstance(topic, str), type(topic)
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

    def desc(self):
        # return description
        _type = str(self.event_filter)
        if _type.startswith("<class '"):
            _type = _type[8:-2]
        return f'"{self.topic}" (type {_type})'
