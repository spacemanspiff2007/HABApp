from collections.abc import Callable
from typing import Any, Final

from HABApp.core.events import EventFilter
from HABApp.core.internals import EventBusListener
from HABApp.core.items import BaseItem


class ListenerCreatorBase:
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any]) -> None:
        self.item: Final = item
        self.callback: Final = callback

        self.listener: EventBusListener | None = None
        self.active = True

    def create_listener(self) -> EventBusListener:
        raise NotImplementedError()

    def listen(self) -> None:
        if not self.active:
            return None

        if self.listener is None:
            self.listener = self.create_listener()

    def cancel(self) -> None:
        if not self.active:
            return None

        if self.listener is not None:
            self.listener.cancel()
            self.listener = None


class EventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], event_filter: EventFilter) -> None:
        super().__init__(item, callback)
        self.event_filter = event_filter

    def create_listener(self) -> EventBusListener:
        return self.item.listen_event(self.callback, self.event_filter)


class NoUpdateEventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], secs: int | float) -> None:
        super().__init__(item, callback)
        self.secs = secs

    def create_listener(self) -> EventBusListener:
        return self.item.watch_update(self.secs).listen_event(self.callback)


class NoChangeEventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], secs: int | float) -> None:
        super().__init__(item, callback)
        self.secs = secs

    def create_listener(self) -> EventBusListener:
        return self.item.watch_change(self.secs).listen_event(self.callback)
