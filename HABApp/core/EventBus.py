import itertools
import logging
import typing

from HABApp.util import PrintException
from . import EventBusListener
from .events import ValueChangeEvent, ValueUpdateEvent

_event_log = logging.getLogger('HABApp.EventBus')
_habapp_log = logging.getLogger('HABApp')


_EVENT_LISTENER: typing.Dict[str, typing.List[EventBusListener]] = {}
_EVENT_LISTENER_ALL_EVENTS: typing.List[EventBusListener] = []


def __get_listener_description(listener: EventBusListener) -> str:
    if listener.name is None:
        return f'all names (type {listener.event_filter})'
    else:
        return f'"{listener.name}" (type {listener.event_filter})'


class ComplexEventValue:
    def __init__(self, value):
        self.value: typing.Any = value


@PrintException
def post_event(name, event):

    _event_log.info(event)

    # Sometimes we have nested data structures which we need to set the value.
    # Once the value in the item registry is set the data structures provide no benefit thus
    # we unpack the corresponding value
    if isinstance(event, (ValueUpdateEvent, ValueChangeEvent)):
        if isinstance(event.value, ComplexEventValue):
            event.value = event.value.value

    # Notify all listeners
    for listener in itertools.chain(_EVENT_LISTENER.get(name, []), _EVENT_LISTENER_ALL_EVENTS):
        listener.notify_listeners(event)

    return None


def add_listener(listener: EventBusListener):
    assert isinstance(listener, EventBusListener)
    add_to_all = listener.name is None

    item_listeners = _EVENT_LISTENER.setdefault(listener.name, []) if not add_to_all else _EVENT_LISTENER_ALL_EVENTS

    # don't add the same listener twice
    if listener in item_listeners:
        _habapp_log.warning(f'Event listener for {__get_listener_description(listener)} has already been added!')
        return None

    # add listener
    item_listeners.append( listener)
    _habapp_log.debug(f'Added event listener for {__get_listener_description(listener)}')
    return None


def remove_listener(listener: EventBusListener):
    assert isinstance(listener, EventBusListener)
    add_to_all = listener.name is None

    item_listeners = _EVENT_LISTENER.get(listener.name, []) if not add_to_all else _EVENT_LISTENER_ALL_EVENTS

    # print warning if we try to remove it twice
    if listener not in item_listeners:
        _habapp_log.warning(f'Event listener for {__get_listener_description(listener)} has already been removed!')
        return None

    # remove listener
    item_listeners.remove(listener)
    _habapp_log.debug(f'Removed event listener for {__get_listener_description(listener)}')


def remove_all_listeners():
    _EVENT_LISTENER.clear()
    _EVENT_LISTENER_ALL_EVENTS.clear()
