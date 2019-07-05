from . import WrappedFunction
from .events import AllEvents


class EventBusListener:
    def __init__(self, name, callback, event_type=AllEvents):
        assert isinstance(name, str) or name is None, type(name)
        assert isinstance(callback, WrappedFunction)

        self.name: str = name
        self.func = callback

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
