from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, Json
from typing_extensions import Self, override

from HABApp.openhab.events.item_events import GroupStateChangedEvent as TargetGroupStateChangedEvent
from HABApp.openhab.events.item_events import GroupStateUpdatedEvent as TargetGroupStateUpdatedEvent
from HABApp.openhab.events.item_events import ItemAddedEvent as TargetItemAddedEvent
from HABApp.openhab.events.item_events import ItemCommandEvent as TargetItemCommandEvent
from HABApp.openhab.events.item_events import ItemRemovedEvent as TargetItemRemovedEvent
from HABApp.openhab.events.item_events import ItemStateChangedEvent as TargetItemStateChangedEvent
from HABApp.openhab.events.item_events import ItemStateEvent as TargetItemStateEvent
from HABApp.openhab.events.item_events import ItemStatePredictedEvent as TargetItemStatePredictedEvent
from HABApp.openhab.events.item_events import ItemStateUpdatedEvent as TargetItemStateUpdatedEvent
from HABApp.openhab.events.item_events import ItemUpdatedEvent as TargetItemUpdatedEvent

from .base import SERIALIZE_TO_JSON_STR, BaseEvent, BaseModel, BaseOutEvent
from .item_value_types import OpenHabValueType, OpenHabValueTypeAdapter


class ValueChangedPayload(BaseModel):
    type: str
    value: str
    old_type: str = Field(alias='oldType')
    old_value: str = Field(alias='oldValue')


class ItemStateEvent(BaseEvent):
    type: Literal['ItemStateEvent']
    payload: Json[OpenHabValueType]

    @override
    def to_event(self) -> TargetItemStateEvent:
        payload = self.payload
        return TargetItemStateEvent(
            name=self.topic[14:-6], value=payload.get_value()
        )


class ItemStateUpdatedEvent(BaseEvent):
    type: Literal['ItemStateUpdatedEvent']
    payload: Json[OpenHabValueType]

    @override
    def to_event(self) -> TargetItemStateUpdatedEvent:
        payload = self.payload
        return TargetItemStateUpdatedEvent(
            name=self.topic[14:-13], value=payload.get_value()
        )


class ItemStateChangedEvent(BaseEvent):
    type: Literal['ItemStateChangedEvent']
    payload: Json[ValueChangedPayload]

    @override
    def to_event(self) -> TargetItemStateChangedEvent:
        payload = self.payload
        new = (ta := OpenHabValueTypeAdapter).validate_python({'type': payload.type, 'value': payload.value})
        old = ta.validate_python({'type': payload.old_type, 'value': payload.old_value})
        return TargetItemStateChangedEvent(
            name=self.topic[14:-13],
            value=new.get_value(),
            old_value=old.get_value()
        )


class ItemCommandEvent(BaseEvent):
    type: Literal['ItemCommandEvent']
    payload: Json[OpenHabValueType]

    @override
    def to_event(self) -> TargetItemCommandEvent:
        payload = self.payload
        return TargetItemCommandEvent(
            name=self.topic[14:-8], value=payload.get_value()
        )


class PredictedPayloadModel(BaseModel):
    type: str = Field(alias='predictedType')
    value: str = Field(alias='predictedValue')
    is_confirmation: bool = Field(alias='isConfirmation')


class ItemStatePredictedEvent(BaseEvent):
    type: Literal['ItemStatePredictedEvent']
    payload: Json[PredictedPayloadModel]

    @override
    def to_event(self) -> TargetItemStatePredictedEvent:
        payload = self.payload
        value = OpenHabValueTypeAdapter.validate_python({'type': payload.type, 'value': payload.value})
        return TargetItemStatePredictedEvent(
            name=self.topic[14:-15], value=value.get_value(), is_confirmation=payload.is_confirmation
        )


class GroupStateUpdatedEvent(BaseEvent):
    type: Literal['GroupStateUpdatedEvent']
    payload: Json[OpenHabValueType]

    @override
    def to_event(self) -> TargetGroupStateUpdatedEvent:
        parts = self.topic.split('/')
        payload = self.payload
        return TargetGroupStateUpdatedEvent(
            name=parts[2], item=parts[3], value=payload.get_value()
        )


class GroupStateChangedEvent(BaseEvent):
    type: Literal['GroupItemStateChangedEvent']
    payload: Json[ValueChangedPayload]

    @override
    def to_event(self) -> TargetGroupStateChangedEvent:
        parts = self.topic.split('/')
        payload = self.payload
        new = (ta := OpenHabValueTypeAdapter).validate_python({'type': payload.type, 'value': payload.value})
        old = ta.validate_python({'type': payload.old_type, 'value': payload.old_value})
        return TargetGroupStateChangedEvent(
            name=parts[2], item=parts[3],
            value=new.get_value(),
            old_value=old.get_value()
        )


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/ItemDTO.java
class ItemDtoModel(BaseModel):
    type: str
    name: str
    label: str | None = None
    category: str | None = None
    tags: frozenset[str]
    groups: frozenset[str] = Field(alias='groupNames')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/GroupFunctionDTO.java
class GroupFunctionDTOModel(BaseModel):
    name: str
    params: tuple[str, ...]


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/GroupItemDTO.java
class GroupItemDtoModel(ItemDtoModel):
    group_type: str | None = Field(default=None, alias='groupType')
    group_function: GroupFunctionDTOModel | None = Field(default=None, alias='function')


# https://github.com/openhab/openhab-core/blob/ce374252fa2c821103da888302f930c1c127f73c/bundles/org.openhab.core/src/main/java/org/openhab/core/items/events/ItemAddedEvent.java
class ItemAddedEvent(BaseEvent):
    type: Literal['ItemAddedEvent']
    payload: Json[GroupItemDtoModel]

    @override
    def to_event(self) -> TargetItemAddedEvent:
        payload = self.payload
        return TargetItemAddedEvent(
            type=payload.type, name=payload.name, label=payload.label, tags=payload.tags, group_names=payload.groups
        )


class ItemUpdatedEvent(BaseEvent):
    type: Literal['ItemUpdatedEvent']
    payload: Json[tuple[GroupItemDtoModel, GroupItemDtoModel]]

    @override
    def to_event(self) -> TargetItemUpdatedEvent:
        new, old = self.payload
        return TargetItemUpdatedEvent(
            type=new.type, name=new.name, label=new.label, tags=new.tags, group_names=new.groups
        )


class ItemRemovedEvent(BaseEvent):
    type: Literal['ItemRemovedEvent']
    payload: Json[GroupItemDtoModel]

    @override
    def to_event(self) -> TargetItemRemovedEvent:
        payload = self.payload
        return TargetItemRemovedEvent(
            type=payload.type, name=payload.name, label=payload.label, tags=payload.tags, groups=payload.groups
        )


# ----------------------------------------------------------------------------------------------------------------------
# Outgoing events
# ----------------------------------------------------------------------------------------------------------------------
class ItemStateSendEvent(BaseOutEvent):
    type: Literal['ItemStateEvent'] = 'ItemStateEvent'
    topic: str
    payload: Annotated[OpenHabValueType, SERIALIZE_TO_JSON_STR]

    @classmethod
    def create(cls, name: str, payload: OpenHabValueType) -> Self:
        return cls(
            type='ItemStateEvent', topic=f'openhab/items/{name:s}/state', payload=payload
        )


class ItemCommandSendEvent(BaseOutEvent):
    type: Literal['ItemCommandEvent'] = 'ItemCommandEvent'
    topic: str
    payload: Annotated[OpenHabValueType, SERIALIZE_TO_JSON_STR]

    @classmethod
    def create(cls, name: str, payload: OpenHabValueType) -> Self:
        return cls(
            type='ItemCommandEvent', topic=f'openhab/items/{name:s}/command', payload=payload
        )
