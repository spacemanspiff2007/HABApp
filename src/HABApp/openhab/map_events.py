from typing import Dict, Type
from HABApp.core.const.json import load_json

from .events import OpenhabEvent, \
    ItemStateEvent, ItemStateUpdatedEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent, \
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, \
    GroupStateUpdatedEvent, GroupStateChangedEvent, \
    ChannelTriggeredEvent, ChannelDescriptionChangedEvent, \
    ThingAddedEvent, ThingRemovedEvent, ThingUpdatedEvent, \
    ThingStatusInfoChangedEvent, ThingStatusInfoEvent, ThingFirmwareStatusInfoEvent, \
    ThingConfigStatusInfoEvent


EVENT_LIST = [
    # item events
    ItemStateEvent, ItemStateUpdatedEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent,
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent,

    GroupStateUpdatedEvent, GroupStateChangedEvent,

    # channel events
    ChannelTriggeredEvent, ChannelDescriptionChangedEvent,

    # thing events
    ThingAddedEvent, ThingRemovedEvent, ThingUpdatedEvent,
    ThingStatusInfoEvent, ThingStatusInfoChangedEvent,
    ThingFirmwareStatusInfoEvent,
    ThingConfigStatusInfoEvent,
]

_events: Dict[str, Type[OpenhabEvent]] = {k.__name__: k for k in EVENT_LIST}
_events['GroupItemStateChangedEvent'] = GroupStateChangedEvent       # Naming from openHAB is inconsistent here
_events['FirmwareStatusInfoEvent'] = ThingFirmwareStatusInfoEvent    # Naming from openHAB is inconsistent here
_events['ConfigStatusInfoEvent'] = ThingConfigStatusInfoEvent        # Naming from openHAB is inconsistent here


def get_event(_in_dict: dict) -> OpenhabEvent:
    event_type: str = _in_dict['type']
    topic: str = _in_dict['topic']
    payload: dict = load_json(_in_dict['payload'])

    # Find event from implemented events
    try:
        return _events[event_type].from_dict(topic, payload)
    except KeyError:
        msg = f'Unknown Event: {event_type:s} for {_in_dict}'
        raise ValueError(msg) from None
