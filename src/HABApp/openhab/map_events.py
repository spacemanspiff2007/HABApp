from typing import Dict, Type
from HABApp.core.const.json import load_json

from .events import OpenhabEvent, \
    ItemStateEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent, \
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, GroupItemStateChangedEvent, \
    ChannelTriggeredEvent, ChannelDescriptionChangedEvent, \
    ThingAddedEvent, ThingRemovedEvent, ThingUpdatedEvent, \
    ThingStatusInfoChangedEvent, ThingStatusInfoEvent, ThingFirmwareStatusInfoEvent, \
    ThingConfigStatusInfoEvent


EVENT_LIST = [
    # item events
    ItemStateEvent, ItemStateChangedEvent, ItemCommandEvent, ItemAddedEvent,
    ItemUpdatedEvent, ItemRemovedEvent, ItemStatePredictedEvent, GroupItemStateChangedEvent,

    # channel events
    ChannelTriggeredEvent, ChannelDescriptionChangedEvent,

    # thing events
    ThingAddedEvent, ThingRemovedEvent, ThingUpdatedEvent,
    ThingStatusInfoEvent, ThingStatusInfoChangedEvent,
    ThingFirmwareStatusInfoEvent,
    ThingConfigStatusInfoEvent,
]

_events: Dict[str, Type[OpenhabEvent]] = {k.__name__: k for k in EVENT_LIST}
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
        raise ValueError(f'Unknown Event: {event_type:s} for {_in_dict}')
