from typing import Any, Callable, List, Optional, Tuple

from HABApp.core.event_bus_listener import EventBusListener
from HABApp.core.events import AllEvents, EventFilter
from HABApp.core.items.base_valueitem import BaseItem


class EventListenerGroup:
    """Helper to create/cancel multiple event listeners simultaneously
    """
    def __init__(self, default_callback: Optional[Callable[[Any], Any]] = None, default_event_filter=AllEvents):
        self._items: List[Tuple[BaseItem, Callable[[Any], Any], EventFilter]] = []
        self._subs: List[EventBusListener] = []

        self._is_active = False

        self._default_callback = default_callback
        self._default_event_filter = default_event_filter

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

        self._items.append((item, callback, event_filter if event_filter is not None else AllEvents))
        if self._is_active:
            self._subs.append(item.listen_event(callback, event_filter))
        return self
