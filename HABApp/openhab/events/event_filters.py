from HABApp.core.events import ValueChangeEventFilter, ValueUpdateEventFilter
from . import ItemStateChangedEvent, ItemStateEvent


class ItemStateEventFilter(ValueUpdateEventFilter):
    _EVENT_TYPE = ItemStateEvent


class ItemStateChangedEventFilter(ValueChangeEventFilter):
    _EVENT_TYPE = ItemStateChangedEvent
