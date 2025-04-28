from typing import Annotated

from pydantic import Field, TypeAdapter

from .channel_events import ChannelDescriptionChangedEvent, ChannelTriggeredEvent
from .item_events import (
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
)
from .thing_events import (
    ThingAddedEvent,
    ThingConfigStatusInfoEvent,
    ThingFirmwareStatusInfoEvent,
    ThingRemovedEvent,
    ThingStatusInfoChangedEvent,
    ThingStatusInfoEvent,
    ThingUpdatedEvent,
)
from .websocket_events import WebsocketEventType


OPENHAB_EVENT_TYPE = Annotated[
    ChannelTriggeredEvent |
    ChannelDescriptionChangedEvent |
    GroupStateChangedEvent |
    GroupStateUpdatedEvent |
    ItemAddedEvent |
    ItemCommandEvent |
    ItemRemovedEvent |
    ItemStateChangedEvent |
    ItemStateEvent |
    ItemStatePredictedEvent |
    ItemStateUpdatedEvent |
    ItemUpdatedEvent |
    ThingAddedEvent |
    ThingConfigStatusInfoEvent |
    ThingFirmwareStatusInfoEvent |
    ThingRemovedEvent |
    ThingStatusInfoChangedEvent |
    ThingStatusInfoEvent |
    ThingUpdatedEvent |
    WebsocketEventType,
    Field(discriminator='type')
]


OPENHAB_EVENT_TYPE_ADAPTER = TypeAdapter[OPENHAB_EVENT_TYPE](OPENHAB_EVENT_TYPE)
