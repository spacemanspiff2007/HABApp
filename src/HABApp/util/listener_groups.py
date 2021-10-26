from typing import Any, Callable, List, Optional, Union

from HABApp.core.event_bus_listener import EventBusListener
from HABApp.core.events import AllEvents, EventFilter
from HABApp.core.items.base_valueitem import BaseItem


class EventListenerCreator:
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any],  event_filter: EventFilter):
        self.item = item
        self.callback = callback
        self.event_filter = event_filter

    def listen(self) -> EventBusListener:
        return self.item.listen_event(self.callback, self.event_filter)


class NoUpdateEventListenerCreator:
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], secs: Union[int, float]):
        self.item = item
        self.callback = callback
        self.secs = secs

    def listen(self) -> EventBusListener:
        return self.item.watch_update(self.secs).listen_event(self.callback)


class NoChangeEventListenerCreator:
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], secs: Union[int, float]):
        self.item = item
        self.callback = callback
        self.secs = secs

    def listen(self) -> EventBusListener:
        return self.item.watch_change(self.secs).listen_event(self.callback)


class EventListenerGroup:
    """Helper to create/cancel multiple event listeners simultaneously
    """
    def __init__(self, default_callback: Optional[Callable[[Any], Any]] = None, default_event_filter=AllEvents,
                 default_seconds: Optional[Union[int, float]] = None):
        self._items: List[Union[EventListenerCreator, NoUpdateEventListenerCreator, NoChangeEventListenerCreator]] = []
        self._subs: List[EventBusListener] = []

        self._is_active = False

        self._default_callback = default_callback
        self._default_event_filter = default_event_filter
        self._default_seconds = default_seconds

    @property
    def active(self):
        return self._is_active

    def listen(self):
        """Create all event listeners. If the event listeners are already active this will do nothing.
        """
        if self._is_active:
            return None
        self._is_active = True

        for obj in self._items:
            self._subs.append(obj.listen())

    def cancel(self):
        """Cancel the active event listeners. If the event listeners are not active this will do nothing.
        """
        if not self._is_active:
            return None
        self._is_active = False

        while self._subs:
            self._subs.pop().cancel()

    def add_listener(self, item: BaseItem, callback: Optional[Callable[[Any], Any]] = None,
                     event_filter: Optional[EventFilter] = None) -> 'EventListenerGroup':
        """Add an event listener to the group

        :param item: Item
        :param callback: Callback or default callback if omitted
        :param event_filter: Event filter of default event filter if omitted
        :return: self
        """
        if callback is None:
            callback = self._default_callback
        if callback is None:
            raise ValueError('No callback passed and no default callback specified in __init__')

        if event_filter is None:
            event_filter = self._default_event_filter

        obj = EventListenerCreator(item, callback, event_filter if event_filter is not None else AllEvents)
        self._items.append(obj)

        if self._is_active:
            self._subs.append(obj.listen())
        return self

    def add_no_update_watcher(self, item: BaseItem, callback: Optional[Callable[[Any], Any]] = None,
                              seconds: Optional[Union[int, float]] = None) -> 'EventListenerGroup':
        """Add an no update watcher to the group. On ``listen`` this will create a no update watcher and
         the corresponding event listener that will trigger the callback

        :param item: Item
        :param callback: Callback or default callback if omitted
        :param seconds: No update time for the no update watcher or default seconds if omitted
        :return: self
        """
        if callback is None:
            callback = self._default_callback
        if seconds is None:
            seconds = self._default_seconds

        if callback is None:
            raise ValueError('No callback passed and no default callback specified in __init__')
        if seconds is None:
            raise ValueError('No seconds passed and no default seconds specified in __init__')

        obj = NoUpdateEventListenerCreator(item, callback, seconds)
        self._items.append(obj)

        if self._is_active:
            self._subs.append(obj.listen())
        return self

    def add_no_change_watcher(self, item: BaseItem, callback: Optional[Callable[[Any], Any]] = None,
                              seconds: Optional[Union[int, float]] = None) -> 'EventListenerGroup':
        """Add an no change watcher to the group. On ``listen`` this this will create a no change watcher and
         the corresponding event listener that will trigger the callback

        :param item: Item
        :param callback: Callback or default callback if omitted
        :param seconds: No update time for the no change watcher or default seconds if omitted
        :return: self
        """
        if callback is None:
            callback = self._default_callback
        if seconds is None:
            seconds = self._default_seconds

        if callback is None:
            raise ValueError('No callback passed and no default callback specified in __init__')
        if seconds is None:
            raise ValueError('No seconds passed and no default seconds specified in __init__')

        obj = NoChangeEventListenerCreator(item, callback, seconds)
        self._items.append(obj)

        if self._is_active:
            self._subs.append(obj.listen())
        return self
