from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Json

from .events import (
    ChannelDescriptionChangedEvent,
    ChannelTriggeredEvent,
    GroupStateChangedEvent,
    GroupStateUpdatedEvent,
    ItemAddedEvent,
    ItemCommandEvent,
    ItemRemovedEvent,
    ItemStateChangedEvent,
    ItemStateEvent,
    ItemStatePredictedEvent,
    ItemStateUpdatedEvent,
    ItemUpdatedEvent,
    OpenhabEvent,
    ThingAddedEvent,
    ThingConfigStatusInfoEvent,
    ThingFirmwareStatusInfoEvent,
    ThingRemovedEvent,
    ThingStatusInfoChangedEvent,
    ThingStatusInfoEvent,
    ThingUpdatedEvent,
)


EVENT_LIST: Final = (
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
)

_events: dict[str, type[OpenhabEvent]] = {k.__name__: k for k in EVENT_LIST}
_events['GroupItemStateChangedEvent'] = GroupStateChangedEvent       # Naming from openHAB is inconsistent here
_events['FirmwareStatusInfoEvent'] = ThingFirmwareStatusInfoEvent    # Naming from openHAB is inconsistent here
_events['ConfigStatusInfoEvent'] = ThingConfigStatusInfoEvent        # Naming from openHAB is inconsistent here


class OpenHABEventModel(BaseModel):
    model_config = ConfigDict(extra='forbid')

    type: str
    topic: str
    payload: Json[dict[str, Any] | tuple[dict[str, Any], ...]]


def get_event(_in_dict: dict) -> OpenhabEvent:

    m = OpenHABEventModel.model_validate(_in_dict)

    # Find event from implemented events
    try:
        return _events[m.type].from_dict(m.topic, m.payload)
    except KeyError:
        msg = f'Unknown Event: {m.type:s} for {_in_dict}'
        raise ValueError(msg) from None
