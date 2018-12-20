import logging
import typing

from HABApp.util import PrintException

log = logging.getLogger('HABApp.Events')


class ValueUpdateEvent:
    def __init__(self, name = None, value = None):
        self.name : str = name
        self.value = value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ValueChangeEvent:
    def __init__(self, name = None, value = None, old_value = None):
        self.name : str = name
        self.value = value
        self.old_value = old_value

    def __repr__(self):
        return f'<{self.__class__.__name__} topic: {self.name}, value: {self.value}, old_value: {self.old_value}>'



class EventListener:
    def __init__(self, name, callback, event_type = None):
        assert isinstance(name, str), type(str)
        assert callable(callback)

        self.name : str = name
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

        self.__event_listener: typing.Dict[str, typing.List[EventListener]]= {}

    @PrintException
    def post_event(self, name, event):

        log.info(event)

        # Update Item Registry BEFORE doing the callbacks
        if isinstance(event, ValueUpdateEvent):
            self.__items.set_state(event.name, event.value)

        # Notify all listeners
        for listener in self.__event_listener.get(name, []):
            if listener.event_matches(event):
                self.__workers.submit(listener.callback, event)
        return None

    def remove_listener(self, listener : EventListener):
        assert isinstance(listener, EventListener)

        item_listeners = self.__event_listener.get(listener.name, [])
        if listener not in item_listeners:
            return None
        item_listeners.remove(listener)
        log.debug(f'Removed event listener for {listener.name} (type {listener.event_filter})')

    def add_listener(self, listener : EventListener):
        assert isinstance(listener, EventListener)

        # don't add the same listener twice
        item_listeners = self.__event_listener.get(listener.name, [])
        if listener in item_listeners:
            return None

        item_listeners.append( listener)
        self.__event_listener[listener.name] = item_listeners

        log.debug(f'Added Event listener for {listener.name} (type {listener.event_filter})')
        return None
