from ..openhab.events import BaseItemEvent, EVENT_LIST

class EventBusListener:
    def __init__(self, item_name, callback, event_type = None):
        assert isinstance(item_name, str), type(str)
        assert callable(callback)

        if event_type is not None:
            assert event_type in EVENT_LIST

        self.item_name : str = item_name
        self.callback = callback

        self.event_filter: BaseItemEvent = event_type

    def event_matches(self, event):
        if self.event_filter is None or isinstance(event, self.event_filter):
            return True
        return False
