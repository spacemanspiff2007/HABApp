import itertools
import logging
import typing

from HABApp.util import PrintException
from . import EventBusListener, ValueUpdateEvent
from .Items import set_item_state as _set_item_state

_event_log = logging.getLogger('HABApp.EventBus')
_habapp_log = logging.getLogger('HABApp')


_EVENT_LISTENER: typing.Dict[str, typing.List[EventBusListener]] = {}
_EVENT_LISTENER_ALL_EVENTS: typing.List[EventBusListener] = []


@PrintException
def post_event(name, event):

    _event_log.info(event)

    # Update Item Registry BEFORE doing the callbacks
    if isinstance(event, ValueUpdateEvent):
        _set_item_state(event.name, event.value)

    # Notify all listeners
    for listener in itertools.chain(_EVENT_LISTENER.get(name, []), _EVENT_LISTENER_ALL_EVENTS):
        listener.notify_listeners(event)

    return None


def add_listener(listener: EventBusListener):
    assert isinstance(listener, EventBusListener)
    add_to_all = listener.name is None

    # don't add the same listener twice
    item_listeners = _EVENT_LISTENER.get(listener.name, []) if not add_to_all else _EVENT_LISTENER_ALL_EVENTS
    if listener in item_listeners:
        return None

    item_listeners.append( listener)
    if add_to_all:
        _habapp_log.debug(f'Added Event listener for all names (type {listener.event_filter})')
    else:
        _EVENT_LISTENER[listener.name] = item_listeners
        _habapp_log.debug(f'Added Event listener for "{listener.name}" (type {listener.event_filter})')
    return None


def remove_listener(listener: EventBusListener):
    assert isinstance(listener, EventBusListener)
    add_to_all = listener.name is None

    item_listeners = _EVENT_LISTENER.get(listener.name, []) if not add_to_all else _EVENT_LISTENER_ALL_EVENTS
    if listener not in item_listeners:
        return None
    item_listeners.remove(listener)

    if add_to_all:
        _habapp_log.debug(f'Removed event listener for all names (type {listener.event_filter})')
    else:
        _habapp_log.debug(f'Removed event listener for "{listener.name}" (type {listener.event_filter})')


def remove_all_listeners():
    _EVENT_LISTENER.clear()
    _EVENT_LISTENER_ALL_EVENTS.clear()
