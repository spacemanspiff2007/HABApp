import itertools
import logging
import typing

from HABApp.util import PrintException
from .event_bus_listener import EventBusListener
from .events import ValueUpdateEvent

event_log = logging.getLogger('HABApp.Events')
habapp_log = logging.getLogger('HABApp')



class EventBus:
    def __init__(self):

        from . import Items
        self.__items = Items

        self.__event_listener: typing.Dict[str, typing.List[EventBusListener]] = {}
        self.__event_listener_all: typing.List[EventBusListener] = []

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

    def remove_listener(self, listener : EventBusListener):
        assert isinstance(listener, EventBusListener)
        add_to_all = listener.name is None

        item_listeners = self.__event_listener.get(listener.name, []) if not add_to_all else self.__event_listener_all
        if listener not in item_listeners:
            return None
        item_listeners.remove(listener)

        if add_to_all:
            habapp_log.debug(f'Removed event listener for all names (type {listener.event_filter})')
        else:
            habapp_log.debug(f'Removed event listener for "{listener.name}" (type {listener.event_filter})')

    def add_listener(self, listener: EventBusListener):
        assert isinstance(listener, EventBusListener)
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
