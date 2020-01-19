from .base_event import OpenhabEvent
from .item_events import ItemStateEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent,\
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, GroupItemStateChangedEvent
from .channel_events import ChannelTriggeredEvent
from .thing_events import ThingStatusInfoChangedEvent, ThingStatusInfoEvent

EVENT_LIST = [
    # item events
    ItemStateEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent,
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, GroupItemStateChangedEvent,

    # channel events
    ChannelTriggeredEvent,

    # thing events
    ThingStatusInfoEvent, ThingStatusInfoChangedEvent,
]

__event_lookup = {k.__name__: k for k in EVENT_LIST}


def get_event(_in_dict : dict) -> OpenhabEvent:
    event_type = _in_dict['type']
    try:
        return __event_lookup[event_type](_in_dict)
    except KeyError:
        raise ValueError(f'Unknown Event: {event_type:s} for {_in_dict}')
