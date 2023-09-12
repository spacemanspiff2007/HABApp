import logging
import threading
from typing import Any, TypeVar
from typing import Dict, List

from HABApp.core.events import ComplexEventValue, ValueChangeEvent
from .base_listener import EventBusBaseListener
from HABApp.core.const.log import TOPIC_EVENTS

event_log = logging.getLogger(TOPIC_EVENTS)
habapp_log = logging.getLogger('HABApp')

_TYPE_LISTENER = TypeVar('_TYPE_LISTENER', bound=EventBusBaseListener)


class EventBus:
    def __init__(self):
        self._lock = threading.Lock()
        self._listeners: Dict[str, List[EventBusBaseListener]] = {}

    def post_event(self, topic: str, event: Any):
        assert isinstance(topic, str), type(topic)

        if not isinstance(event, str):
            event_prv = str(event)
        else:
            event_prv = event[:120] + ' ...' if len(event) > 120 else event
            event_prv = "'" + event_prv.replace('\n', '\\n') + "'"

        event_log.info(f'{topic:>20s}: {event_prv}')

        # Sometimes we have nested data structures which we need to set the value.
        # Once the value in the item registry is updated the data structures provide no benefit thus
        # we unpack the corresponding value
        try:
            if isinstance(event.value, ComplexEventValue):
                event.value = event.value.value
            if isinstance(event, ValueChangeEvent) and isinstance(event.old_value, ComplexEventValue):
                event.old_value = event.old_value.value
        except AttributeError:
            pass

        # Notify all listeners
        listeners = self._listeners.get(topic, None)
        if listeners is not None:
            for listener in listeners:
                listener.notify_listeners(event)
        return None

    def add_listener(self, listener: _TYPE_LISTENER):
        assert isinstance(listener, EventBusBaseListener)
        assert isinstance(listener.topic, str) and listener.topic

        with self._lock:
            item_listeners = self._listeners.setdefault(listener.topic, [])

            # don't add the same listener twice
            if listener in item_listeners:
                habapp_log.warning(f'Event listener for {listener.describe()} has already been added!')
                return None

            # add listener
            item_listeners.append(listener)
            habapp_log.debug(f'Added event listener for {listener.describe()}')
            return None

    def remove_listener(self, listener: _TYPE_LISTENER):
        assert isinstance(listener, EventBusBaseListener)
        assert isinstance(listener.topic, str) and listener.topic

        with self._lock:
            item_listeners = self._listeners.get(listener.topic, [])

            # print warning if we try to remove it twice
            if listener not in item_listeners:
                habapp_log.warning(f'Event listener for {listener.describe()} has already been removed!')
                return None

            # remove listener
            item_listeners.remove(listener)
            habapp_log.debug(f'Removed event listener for {listener.describe()}')
            return None

    def remove_all_listeners(self):
        with self._lock:
            self._listeners.clear()
