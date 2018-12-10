import logging
import traceback
import typing
import ujson

import HABApp
from HABApp.openhab.events import get_event
from HABApp.util import PrintException
from . import EventBusListener

log = logging.getLogger('HABApp.Events')


class EventBus:
    def __init__(self, parent):
        assert isinstance(parent, HABApp.habapp.Runtime)
        self.runtime = parent

        self.__event_listener = {}  # type: typing.Dict[str, typing.List[EventBusListener]]

    @PrintException
    def post_event(self, _in : str):
        try:
            event = ujson.loads(_in)
            if log.isEnabledFor(logging.DEBUG):
                log._log(logging.DEBUG, event, [])
            event = get_event(event)
        except Exception as e:
            log.error("{}".format(e))
            for l in traceback.format_exc().splitlines():
                log.error(l)
            return None

        log.info(event)

        # Update Item Registry BEFORE doing the callbacks
        if isinstance(event, HABApp.openhab.events.ItemStateEvent):
            self.runtime.all_items.set_state(event.item, event.value)

        # Notify all listeners
        for listener in self.__event_listener.get(event.item, []):
            if listener.event_matches(event):
                self.runtime.workers.submit(listener.callback, event)
        return None

    def remove_listener(self, listener : EventBusListener):
        assert isinstance(listener, EventBusListener)

        item_listeners = self.__event_listener.get(listener.item_name, [])
        if listener not in item_listeners:
            return None
        item_listeners.remove(listener)
        log.debug(f'Removed event listener for {listener.item_name} (type {listener.event_filter})')


    def add_listener(self, listener : EventBusListener):
        assert isinstance(listener, EventBusListener)

        # don't add the same listener twice
        item_listeners = self.__event_listener.get(listener.item_name, [])
        if listener in item_listeners:
            return None

        item_listeners.append( listener)
        self.__event_listener[listener.item_name] = item_listeners

        log.debug(f'Added Event listener for {listener.item_name} (type {listener.event_filter})')
        return None