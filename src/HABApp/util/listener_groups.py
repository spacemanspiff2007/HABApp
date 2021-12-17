from typing import Any, Callable, Dict, Iterable, Optional, Union

from HABApp.core.event_bus_listener import EventBusListener
from HABApp.core.events import EventFilter
from HABApp.core.items.base_valueitem import BaseItem


class ListenerCreatorBase:
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any]):
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
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any],  event_filter: EventFilter):
        super(EventListenerCreator, self).__init__(item, callback)
        self.event_filter = event_filter

    def create_listener(self) -> EventBusListener:
        return self.item.listen_event(self.callback, self.event_filter)


class NoUpdateEventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], secs: Union[int, float]):
        super(NoUpdateEventListenerCreator, self).__init__(item, callback)
        self.secs = secs

    def create_listener(self) -> EventBusListener:
        return self.item.watch_update(self.secs).listen_event(self.callback)


class NoChangeEventListenerCreator(ListenerCreatorBase):
    def __init__(self, item: BaseItem, callback: Callable[[Any], Any], secs: Union[int, float]):
        super(NoChangeEventListenerCreator, self).__init__(item, callback)
        self.secs = secs

    def create_listener(self) -> EventBusListener:
        return self.item.watch_change(self.secs).listen_event(self.callback)


class ListenerCreatorNotFoundError(Exception):
    pass


class EventListenerGroup:
    """Helper to create/cancel multiple event listeners simultaneously
    """

    def __init__(self):
        self._items: Dict[str, ListenerCreatorBase] = {}
        self._is_active = False

    @property
    def active(self) -> bool:
        """

        :return: True if the listeners are currently active
        """
        return self._is_active

    def listen(self):
        """Create all event listeners. If the event listeners are already active this will do nothing.
        """
        if self._is_active:
            return None
        self._is_active = True

        for o in self._items.values():
            o.listen()

    def cancel(self):
        """Cancel the active event listeners. If the event listeners are not active this will do nothing.
        """
        if not self._is_active:
            return None
        self._is_active = False

        for o in self._items.values():
            o.cancel()

    def activate_listener(self, name: str):
        """Resume a previously deactivated listener creator in the group.

        :param name: item name or alias of the listener
        :return: True if it was activated, False if it was already active
        """
        try:
            obj = self._items[name]
        except KeyError:
            raise ListenerCreatorNotFoundError(f'ListenerCreator for "{name}" not found!') from None
        if obj.active:
            return False

        obj.active = True
        if self._is_active:
            obj.listen()
        return True

    def deactivate_listener(self, name: str, cancel_if_active=True):
        """Exempt the listener creator from further listener/cancel calls

        :param name: item name or alias of the listener
        :param cancel_if_active: Cancel the listener if it is active
        :return: True if it was deactivated, False if it was already deactivated
        """
        try:
            obj = self._items[name]
        except KeyError:
            raise ListenerCreatorNotFoundError(f'ListenerCreator for "{name}" not found!') from None
        if not obj.active:
            return False

        obj.active = False
        if cancel_if_active:
            obj.cancel()
        return True

    def __add_objs(self, cls, item: Union[BaseItem, Iterable[BaseItem]], callback: Callable[[Any], Any],
                   arg, alias: Optional[str] = None):
        # alias -> single param
        if alias is not None:
            if not isinstance(item, BaseItem):
                raise ValueError('Only a single item can be passed together with alias')

        if isinstance(item, BaseItem):
            item = [item]

        for _item in item:
            name = _item.name if alias is None else alias
            self._items[name] = obj = cls(_item, callback, arg)
            if self._is_active:
                obj.listen()

    def add_listener(self, item: Union[BaseItem, Iterable[BaseItem]], callback: Callable[[Any], Any],
                     event_filter: EventFilter, alias: Optional[str] = None) -> 'EventListenerGroup':
        """Add an event listener to the group

        :param item: Single or multiple items
        :param callback: Callback for the item(s)
        :param event_filter: Event filter for the item(s)
        :param alias: Alias if an item with the same name does already exist (e.g. if different callbacks shall be
                      created for the same item)
        :return: self
        """

        self.__add_objs(EventListenerCreator, item, callback, event_filter, alias)
        return self

    def add_no_update_watcher(self, item: Union[BaseItem, Iterable[BaseItem]], callback: Callable[[Any], Any],
                              seconds: Union[int, float], alias: Optional[str] = None) -> 'EventListenerGroup':
        """Add an no update watcher to the group. On ``listen`` this will create a no update watcher and
         the corresponding event listener that will trigger the callback

        :param item: Single or multiple items
        :param callback: Callback for the item(s)
        :param seconds: No update time for the no update watcher
        :param alias: Alias if an item with the same name does already exist (e.g. if different callbacks shall be
                      created for the same item)
        :return: self
        """
        self.__add_objs(NoUpdateEventListenerCreator, item, callback, seconds, alias)
        return self

    def add_no_change_watcher(self, item: Union[BaseItem, Iterable[BaseItem]], callback: Callable[[Any], Any],
                              seconds: Union[int, float], alias: Optional[str] = None) -> 'EventListenerGroup':
        """Add an no change watcher to the group. On ``listen`` this this will create a no change watcher and
         the corresponding event listener that will trigger the callback

        :param item: Single or multiple items
        :param callback: Callback for the item(s)
        :param seconds: No update time for the no change watcher
        :param alias: Alias if an item with the same name does already exist (e.g. if different callbacks shall be
                      created for the same item)
        :return: self
        """
        self.__add_objs(NoChangeEventListenerCreator, item, callback, seconds, alias)
        return self
