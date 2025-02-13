from typing import Literal

from pydantic import Field, Json
from typing_extensions import override

from HABApp.openhab.events import ChannelDescriptionChangedEvent as TargetChannelDescriptionChangedEvent
from HABApp.openhab.events import ChannelTriggeredEvent as TargetChannelTriggeredEvent

from .base import BaseEvent, BaseModel


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/events/ChannelTriggeredEvent.java
class ChannelEventPayload(BaseModel):
    event: str
    channel: str


class ChannelTriggeredEvent(BaseEvent):
    type: Literal['ChannelTriggeredEvent']
    payload: Json[ChannelEventPayload]

    @override
    def to_event(self) -> TargetChannelTriggeredEvent:
        payload = self.payload
        return TargetChannelTriggeredEvent(
            name=self.topic[17:-10],
            event=payload.event,
            channel=payload.channel,
        )


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/events/ChannelDescriptionChangedEvent.java
class ChannelDescriptionChangedPayload(BaseModel):
    field: str
    name: str = Field(alias='channelUID')
    value: str
    old_value: str | None = Field(None, alias='oldValue')
    linked_items: tuple[str, ...] = Field((), alias='linkedItemNames')


class ChannelDescriptionChangedEvent(BaseEvent):
    type: Literal['ChannelDescriptionChangedEvent']
    payload: Json[ChannelDescriptionChangedPayload]

    @override
    def to_event(self) -> TargetChannelDescriptionChangedEvent:
        payload = self.payload
        return TargetChannelDescriptionChangedEvent(
            name=self.topic[17:-19],
            field=payload.field,
            value=payload.value,
        )
