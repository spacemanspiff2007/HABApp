from typing import Any, Callable, Iterable, List, Optional, Tuple

from HABApp.core.event_bus_listener import EventBusListener
from HABApp.core.events import AllEvents, EventFilter
from HABApp.core.items.base_valueitem import BaseItem


class EventListenerGroup:
    """Helper to create/cancel multiple event listeners simultaneously
    """
    def __init__(self, objs: Iterable[Tuple[BaseItem, Callable[[Any], Any], Any]] = tuple()):
        self._items: List[Tuple[BaseItem, Callable[[Any], Any], EventFilter]] = []
        self._subs: List[EventBusListener] = []

        self._is_active = False

        for _item, _cb, _filter in objs:
            self._items.append((_item, _cb, _filter if _filter is not None else AllEvents))

    @property
    def active(self):
        return self._is_active

    def listen(self):
        """Create all event listeners. If the event listeners are already active this will do nothing.
        """
        if self._is_active:
            return None
        self._is_active = True

        for item, callback, event_filter in self._items:
            self._subs.append(item.listen_event(callback, event_filter))

    def cancel(self):
        """Cancel the active event listeners. If the event listeners are not active this will do nothing.
        """
        if not self._is_active:
            return None
        self._is_active = False

        while self._subs:
            self._subs.pop().cancel()

    def add_listener(self, item: BaseItem, callback: Callable[[Any], Any],
                     event_filter: Optional[EventFilter]) -> 'EventListenerGroup':
        """Add an event listener to the group
        
        :param item: Item
        :param callback: Callback
        :param event_filter: Optional filter
        :return: self
        """
        self._items.append((item, callback, event_filter if event_filter is not None else AllEvents))
        if self._is_active:
            self._subs.append(item.listen_event(callback, event_filter))
        return self
