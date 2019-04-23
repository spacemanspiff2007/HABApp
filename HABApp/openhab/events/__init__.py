from .map_events import map_event_types
from .base_event import BaseItemEvent
from .item_events import ItemStateEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent,\
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, GroupItemStateChangedEvent

EVENT_LIST = [ItemStateEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent,
              ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, GroupItemStateChangedEvent]

__event_lookup = { k.__name__ : k for k in EVENT_LIST}

def get_event(_in_dict : dict) -> BaseItemEvent:
    event_type = _in_dict['type']
    try:
        return __event_lookup[event_type](_in_dict)
    except KeyError:
        raise ValueError(f'Unknown Event: {event_type:s}')
