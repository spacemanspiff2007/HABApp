import itertools
import logging
import typing

from HABApp.util import PrintException
from . import EventBusListener
from .events import ComplexEventValue

_event_log = logging.getLogger('HABApp.EventBus')
_habapp_log = logging.getLogger('HABApp')


_EVENT_LISTENER: typing.Dict[str, typing.List[EventBusListener]] = {}
_EVENT_LISTENER_ALL_EVENTS: typing.List[EventBusListener] = []

# todo: make central HABApp topic (name) definition here


def __get_listener_description(listener: EventBusListener) -> str:
    if listener.topic is None:
        return f'all names (type {listener.event_filter})'
    else:
        return f'"{listener.topic}" (type {listener.event_filter})'


@PrintException
def post_event(topic: str, event):
    assert isinstance(topic, str), type(topic)

    _event_log.info(f'{topic:>20s}: {event}')

    # Sometimes we have nested data structures which we need to set the value.
    # Once the value in the item registry is set the data structures provide no benefit thus
    # we unpack the corresponding value
    try:
        if isinstance(event.value, ComplexEventValue):
            event.value = event.value.value
    except AttributeError:
        pass

    # Notify all listeners
    for listener in itertools.chain(_EVENT_LISTENER.get(topic, []), _EVENT_LISTENER_ALL_EVENTS):
        listener.notify_listeners(event)

    return None


def add_listener(listener: EventBusListener):
    assert isinstance(listener, EventBusListener)
    add_to_all = listener.topic is None

    item_listeners = _EVENT_LISTENER.setdefault(listener.topic, []) if not add_to_all else _EVENT_LISTENER_ALL_EVENTS

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
    add_to_all = listener.topic is None

    item_listeners = _EVENT_LISTENER.get(listener.topic, []) if not add_to_all else _EVENT_LISTENER_ALL_EVENTS

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
