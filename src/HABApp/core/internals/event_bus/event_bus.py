import logging
import threading
from typing import Any

from HABApp.core.const.log import TOPIC_EVENTS
from HABApp.core.internals.event_bus.base_listener import EventBusListenerBase


event_log = logging.getLogger(TOPIC_EVENTS)
habapp_log = logging.getLogger('HABApp')


class EventBus:
    __slots__ = ('_listeners', '_lock')

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._listeners: dict[str, tuple[EventBusListenerBase, ...]] = {}

    def post_event(self, topic: str, event: Any) -> None:
        if not isinstance(topic, str):
            msg = f'Topic must be a string! Got {type(topic)}'
            raise TypeError(msg)

        if not isinstance(event, str):
            event_prv = str(event)
        else:
            event_prv = event[:120] + ' ...' if len(event) > 120 else event
            event_prv = "'" + event_prv.replace('\n', '\\n') + "'"

        event_log.info(f'{topic:>20s}: {event_prv}')

        # Notify all listeners
        if (listeners := self._listeners.get(topic)) is not None:
            for listener in listeners:
                listener.notify_listeners(event)
        return None

    def add_listener(self, listener: EventBusListenerBase) -> None:
        if not isinstance(listener, EventBusListenerBase):
            raise TypeError()
        if not isinstance(topic := listener.topic, str):
            raise TypeError()
        if not topic:
            raise ValueError()

        with self._lock:
            item_listeners = self._listeners.get(topic, ())

            # don't add the same listener twice
            if listener in item_listeners:
                habapp_log.warning(f'Event listener for {listener.describe()} has already been added!')
                return None

            # add listener
            self._listeners[topic] = item_listeners + (listener, )
            habapp_log.debug(f'Added event listener for {listener.describe()}')
            return None

    def remove_listener(self, listener: EventBusListenerBase) -> None:
        if not isinstance(listener, EventBusListenerBase):
            raise TypeError()
        if not isinstance(topic := listener.topic, str):
            raise TypeError()
        if not topic:
            raise ValueError()

        with self._lock:
            item_listeners = self._listeners.get(topic, ())

            # print warning if we try to remove it twice
            if listener not in item_listeners:
                habapp_log.warning(f'Event listener for {listener.describe()} has already been removed!')
                return None

            # remove listener
            new_listeners = tuple(o for o in item_listeners if o is not listener)
            if new_listeners:
                self._listeners[topic] = new_listeners
            else:
                self._listeners.pop(topic, None)

            habapp_log.debug(f'Removed event listener for {listener.describe()}')
            return None

    def remove_all_listeners(self) -> None:
        with self._lock:
            self._listeners.clear()
