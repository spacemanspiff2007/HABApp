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
        
        self.__is_all = self.event_filter is AllEvents
        self.__is_single = not isinstance(self.event_filter, (list, tuple, set))

    def notify_listeners(self, event):
        # We run always
        if self.__is_all:
            self.func.run(event)
            return None

        # single filter
        if self.__is_single:
            if isinstance(event, self.event_filter):
                self.func.run(event)
            return None

        # Make it possible to specify multiple classes
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
