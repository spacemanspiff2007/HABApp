from typing import Any, Callable, Dict, Iterable, Optional, Union

from HABApp.core.internals import HINT_EVENT_FILTER_OBJ
from HABApp.core.items import BaseItem, HINT_ITEM_OBJ

from HABApp.core.lib.parameters import TH_POSITIVE_TIME_DIFF
from .listener_creator import ListenerCreatorBase, EventListenerCreator, \
    NoChangeEventListenerCreator, NoUpdateEventListenerCreator


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

        if cancel_if_active:
            obj.cancel()
        obj.active = False
        return True

    def __add_objs(self, cls, item: Union[HINT_ITEM_OBJ, Iterable[HINT_ITEM_OBJ]], callback: Callable[[Any], Any],
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

    def add_listener(self, item: Union[HINT_ITEM_OBJ, Iterable[HINT_ITEM_OBJ]], callback: Callable[[Any], Any],
                     event_filter: HINT_EVENT_FILTER_OBJ, alias: Optional[str] = None) -> 'EventListenerGroup':
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

    def add_no_update_watcher(self, item: Union[HINT_ITEM_OBJ, Iterable[HINT_ITEM_OBJ]], callback: Callable[[Any], Any],
                              seconds: TH_POSITIVE_TIME_DIFF, alias: Optional[str] = None
                              ) -> 'EventListenerGroup':
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

    def add_no_change_watcher(self, item: Union[HINT_ITEM_OBJ, Iterable[HINT_ITEM_OBJ]], callback: Callable[[Any], Any],
                              seconds: TH_POSITIVE_TIME_DIFF, alias: Optional[str] = None
                              ) -> 'EventListenerGroup':
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
