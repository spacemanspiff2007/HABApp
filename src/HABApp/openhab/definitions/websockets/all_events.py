from typing import Annotated, Final

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


# ----------------------------------------------------------------------------------------------------------------------
# CodeGen
# - union:
#     select: {include: 'Event$|WebsocketEventType$'}
#     name: OpenHabEventType
#     adapter: true
#     discriminator: 'type'
# ----------------------------------------------------------------------------------------------------------------------

OpenHabEventType: Final = Annotated[
    ChannelDescriptionChangedEvent |
    ChannelTriggeredEvent |
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
OPENHAB_EVENT_TYPE_ADAPTER: Final[TypeAdapter[OpenHabEventType]] = TypeAdapter(OpenHabEventType)
