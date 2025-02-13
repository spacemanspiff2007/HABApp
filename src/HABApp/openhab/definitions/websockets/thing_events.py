from typing import Any, Literal

from pydantic import Field, Json
from typing_extensions import override

from HABApp.openhab.definitions import ThingStatusDetailEnum, ThingStatusEnum
from HABApp.openhab.events.thing_events import ThingAddedEvent as TargetThingAddedEvent
from HABApp.openhab.events.thing_events import ThingConfigStatusInfoEvent as TargetThingConfigStatusInfoEvent
from HABApp.openhab.events.thing_events import ThingFirmwareStatusInfoEvent as TargetThingFirmwareStatusInfoEvent
from HABApp.openhab.events.thing_events import ThingRemovedEvent as TargetThingRemovedEvent
from HABApp.openhab.events.thing_events import ThingStatusInfoChangedEvent as TargetThingStatusInfoChangedEvent
from HABApp.openhab.events.thing_events import ThingStatusInfoEvent as TargetThingStatusInfoEvent
from HABApp.openhab.events.thing_events import ThingUpdatedEvent as TargetThingUpdatedEvent

from .base import BaseEvent, BaseModel


class StatusPayload(BaseModel):
    status: ThingStatusEnum
    detail: ThingStatusDetailEnum = Field(alias='statusDetail')
    description: str = ''


class ThingStatusInfoEvent(BaseEvent):
    type: Literal['ThingStatusInfoEvent']
    payload: Json[StatusPayload]

    @override
    def to_event(self) -> TargetThingStatusInfoEvent:
        payload = self.payload
        return TargetThingStatusInfoEvent(
            name=self.topic[15:-7], status=payload.status, detail=payload.detail, description=payload.description
        )


class ThingStatusInfoChangedEvent(BaseEvent):
    type: Literal['ThingStatusInfoChangedEvent']
    payload: Json[tuple[StatusPayload, StatusPayload]]

    @override
    def to_event(self) -> TargetThingStatusInfoChangedEvent:
        new, old = self.payload
        return TargetThingStatusInfoChangedEvent(
            name=self.topic[15:-14],
            status=new.status, detail=new.detail, description=new.description,
            old_status=old.status, old_detail=old.detail, old_description=old.description
        )


class ConfigStatusPayloadMessageEntry(BaseModel):
    parameter: str = Field(alias='parameterName')
    type: str


class ConfigStatusPayload(BaseModel):
    messages: tuple[ConfigStatusPayloadMessageEntry, ...] = Field(alias='configStatusMessages')


class ThingConfigStatusInfoEvent(BaseEvent):
    type: Literal['ConfigStatusInfoEvent']
    payload: Json[ConfigStatusPayload]

    @override
    def to_event(self) -> TargetThingConfigStatusInfoEvent:
        messages = self.payload.messages
        return TargetThingConfigStatusInfoEvent(
            name=self.topic[15:-7],
            config_messages={m.parameter: m.type for m in messages}
        )


class ThingRegistryPayload(BaseModel):
    name: str = Field(alias='UID')
    type: str = Field(alias='thingTypeUID')
    label: str = Field(alias='label')
    location: str = Field('', alias='location')
    channels: tuple[dict[str, Any], ...] = ()
    configuration: dict[str, Any] = {}
    properties: dict[str, str] = {}


class ThingAddedEvent(BaseEvent):
    type: Literal['ThingAddedEvent']
    payload: Json[ThingRegistryPayload]

    @override
    def to_event(self) -> TargetThingAddedEvent:
        payload = self.payload
        return TargetThingAddedEvent(
            name=payload.name, thing_type=payload.type, label=payload.label, location=payload.location,
            channels=payload.channels, configuration=payload.configuration, properties=payload.properties
        )


class ThingUpdatedEvent(BaseEvent):
    type: Literal['ThingUpdatedEvent']
    payload: Json[tuple[ThingRegistryPayload, ThingRegistryPayload]]

    @override
    def to_event(self) -> TargetThingUpdatedEvent:
        payload, old = self.payload
        return TargetThingUpdatedEvent(
            name=payload.name, thing_type=payload.type, label=payload.label, location=payload.location,
            channels=payload.channels, configuration=payload.configuration, properties=payload.properties
        )


class ThingRemovedEvent(BaseEvent):
    type: Literal['ThingRemovedEvent']
    payload: Json[ThingRegistryPayload]

    @override
    def to_event(self) -> TargetThingRemovedEvent:
        payload = self.payload
        return TargetThingRemovedEvent(
            name=payload.name, thing_type=payload.type, label=payload.label, location=payload.location,
            channels=payload.channels, configuration=payload.configuration, properties=payload.properties
        )


class ThingFirmwareStatusInfoPayload(BaseModel):
    name: Any = Field(alias='thingUID')
    status: str = Field(alias='firmwareStatus')
    version: Any | None = None


class ThingFirmwareStatusInfoEvent(BaseEvent):
    type: Literal['FirmwareStatusInfoEvent']
    payload: Json[ThingFirmwareStatusInfoPayload]

    @override
    def to_event(self) -> TargetThingFirmwareStatusInfoEvent:
        payload = self.payload
        return TargetThingFirmwareStatusInfoEvent(
            name=self.topic[15:-16], status=payload.status
        )
