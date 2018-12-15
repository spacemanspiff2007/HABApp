import logging
import typing

from HABApp.util import PrintException

log = logging.getLogger('HABApp.Events')


class EventListener:
    def __init__(self, item_name, callback, event_type = None):
        assert isinstance(item_name, str), type(str)
        assert callable(callback)

        self.item_name : str = item_name
        self.callback = callback

        self.event_filter = event_type

    def event_matches(self, event):
        if self.event_filter is None or isinstance(event, self.event_filter):
            return True
        return False



class EventBus:
    def __init__(self):

        from . import Items, Workers
        self.__items = Items
        self.__workers = Workers

        self.__event_listener = {}  # type: typing.Dict[str, typing.List[EventListener]]

    @PrintException
    def post_event(self, name, event, update_state=False):

        log.info(event)

        # Update Item Registry BEFORE doing the callbacks
        # Requires that event has member 'item' and 'value'
        if update_state is True:
            try:
                self.__items.set_state(event.item, event.value)
            except AttributeError:
                self.__items.set_state(event.topic, event.value)

        # Notify all listeners
        for listener in self.__event_listener.get(name, []):
            if listener.event_matches(event):
                self.__workers.submit(listener.callback, event)
        return None

    def remove_listener(self, listener : EventListener):
        assert isinstance(listener, EventListener)

        item_listeners = self.__event_listener.get(listener.item_name, [])
        if listener not in item_listeners:
            return None
        item_listeners.remove(listener)
        log.debug(f'Removed event listener for {listener.item_name} (type {listener.event_filter})')

    def add_listener(self, listener : EventListener):
        assert isinstance(listener, EventListener)

        # don't add the same listener twice
        item_listeners = self.__event_listener.get(listener.item_name, [])
        if listener in item_listeners:
            return None

        item_listeners.append( listener)
        self.__event_listener[listener.item_name] = item_listeners

        log.debug(f'Added Event listener for {listener.item_name} (type {listener.event_filter})')
        return None
