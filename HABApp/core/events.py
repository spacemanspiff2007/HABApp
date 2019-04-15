import logging
import typing
import itertools

from HABApp.util import PrintException
from . import WrappedFunction

event_log = logging.getLogger('HABApp.Events')
habapp_log = logging.getLogger('HABApp')


class AllEvents:
    pass


class ValueUpdateEvent:
    def __init__(self, name = None, value = None):
        self.name: str = name
        self.value = value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ValueChangeEvent:
    def __init__(self, name = None, value = None, old_value = None):
        self.name: str = name
        self.value = value
        self.old_value = old_value

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}, old_value: {self.old_value}>'


class ValueNoChangeEvent:
    def __init__(self, name = None, value = None, seconds = None):
        self.name: str = name
        self.value = value
        self.seconds: int = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class ValueNoUpdateEvent:
    def __init__(self, name = None, value = None, seconds = None):
        self.name: str = name
        self.value = value
        self.seconds: int = seconds

    def __repr__(self):
        return f'<{self.__class__.__name__} name: {self.name}, value: {self.value}>'


class EventListener:
    def __init__(self, name, callback, event_type=AllEvents):
        assert isinstance(name, str) or name is None, type(name)
        assert isinstance(callback, WrappedFunction)

        self.name: str = name
        self.func = callback

        self.event_filter = event_type

    def notify_listeners(self, event):

        if self.event_filter is AllEvents or isinstance(event, self.event_filter):
            self.func.run(event)
            return None

        # Make it possible to specify multiple classes
        if isinstance(self.event_filter, list) or isinstance(self.event_filter, set):
            for cls in self.event_filter:
                if isinstance(event, cls):
                    self.func.run(event)
                    return None


class EventBus:
    def __init__(self):

        from . import Items
        self.__items = Items

        self.__event_listener: typing.Dict[str, typing.List[EventListener]] = {}
        self.__event_listener_all: typing.List[EventListener] = []

    @PrintException
    def post_event(self, name, event):

        event_log.info(event)

        # Update Item Registry BEFORE doing the callbacks
        if isinstance(event, ValueUpdateEvent):
            self.__items.set_state(event.name, event.value)

        # Notify all listeners
        for listener in itertools.chain(self.__event_listener.get(name, []), self.__event_listener_all):
            listener.notify_listeners(event)

        return None

    def remove_listener(self, listener : EventListener):
        assert isinstance(listener, EventListener)
        add_to_all = listener.name is None

        item_listeners = self.__event_listener.get(listener.name, []) if not add_to_all else self.__event_listener_all
        if listener not in item_listeners:
            return None
        item_listeners.remove(listener)

        if add_to_all:
            habapp_log.debug(f'Removed event listener for all names (type {listener.event_filter})')
        else:
            habapp_log.debug(f'Removed event listener for "{listener.name}" (type {listener.event_filter})')

    def add_listener(self, listener : EventListener):
        assert isinstance(listener, EventListener)
        add_to_all = listener.name is None

        # don't add the same listener twice
        item_listeners = self.__event_listener.get(listener.name, []) if not add_to_all else self.__event_listener_all
        if listener in item_listeners:
            return None

        item_listeners.append( listener)
        if add_to_all:
            habapp_log.debug(f'Added Event listener for all names (type {listener.event_filter})')
        else:
            self.__event_listener[listener.name] = item_listeners
            habapp_log.debug(f'Added Event listener for "{listener.name}" (type {listener.event_filter})')
        return None
