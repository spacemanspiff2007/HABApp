from typing import Any, Callable, Optional, Union

from HABApp.core.events import EventFilter
from HABApp.core.internals import EventBusListener
from HABApp.core.items import HINT_ITEM_OBJ


class ListenerCreatorBase:
    def __init__(self, item: HINT_ITEM_OBJ, callback: Callable[[Any], Any]):
        self.item = item
        self.callback = callback

        self.listener: Optional[EventBusListener] = None
        self.active = True

    def create_listener(self) -> EventBusListener:
        raise NotImplementedError()

    def listen(self):
        if not self.active:
            return None

        if self.listener is None:
            self.listener = self.create_listener()

    def cancel(self):
        if not self.active:
            return None

        if self.listener is not None:
            self.listener.cancel()
            self.listener = None


class EventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: HINT_ITEM_OBJ, callback: Callable[[Any], Any], event_filter: EventFilter):
        super(EventListenerCreator, self).__init__(item, callback)
        self.event_filter = event_filter

    def create_listener(self) -> EventBusListener:
        return self.item.listen_event(self.callback, self.event_filter)


class NoUpdateEventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: HINT_ITEM_OBJ, callback: Callable[[Any], Any], secs: Union[int, float]):
        super(NoUpdateEventListenerCreator, self).__init__(item, callback)
        self.secs = secs

    def create_listener(self) -> EventBusListener:
        return self.item.watch_update(self.secs).listen_event(self.callback)


class NoChangeEventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: HINT_ITEM_OBJ, callback: Callable[[Any], Any], secs: Union[int, float]):
        super(NoChangeEventListenerCreator, self).__init__(item, callback)
        self.secs = secs

    def create_listener(self) -> EventBusListener:
        return self.item.watch_change(self.secs).listen_event(self.callback)
