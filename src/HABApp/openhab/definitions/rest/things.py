from typing import Any

from pydantic import BaseModel, Field, TypeAdapter

from HABApp.openhab.definitions import ThingStatusDetailEnum, ThingStatusEnum


class ChannelResp(BaseModel):
    # ChannelDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/dto/ChannelDTO.java

    uid: str
    id: str
    channel_type: str | None = Field(default=None, alias='channelTypeUID')
    item_type: str | None = Field(default=None, alias='itemType')
    kind: str
    label: str = ''
    description: str = ''
    default_tags: tuple[str, ...] = Field(default=tuple, alias='defaultTags')
    properties: dict[str, Any] = {}
    configuration: dict[str, Any] = {}
    auto_update_policy: str = Field(default='', alias='autoUpdatePolicy')

    # EnrichedChannelDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/thing/EnrichedChannelDTO.java
    linked_items: tuple[str, ...] = Field(alias='linkedItems')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/ThingStatusInfo.java
class ThingStatusResp(BaseModel):
    status: ThingStatusEnum
    detail: ThingStatusDetailEnum = Field(alias='statusDetail')
    description: str | None = None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/firmware/dto/FirmwareStatusDTO.java
class FirmwareStatusResp(BaseModel):
    status: str
    updatable_version: str | None = Field(default=None, alias='updatableVersion')


class ThingResp(BaseModel):
    # AbstractThingDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/dto/AbstractThingDTO.java
    label: str = ''
    bridge_uid: str | None = Field(default=None, alias='bridgeUID')
    configuration: dict[str, Any] = {}
    properties: dict[str, str] = {}
    uid: str = Field(alias='UID')
    thing_type: str = Field(alias='thingTypeUID')
    location: str = ''

    # EnrichedThingDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/thing/EnrichedThingDTO.java
    channels: tuple[ChannelResp, ...] = []
    status: ThingStatusResp = Field(alias='statusInfo')
    firmware_status: FirmwareStatusResp | None = None
    editable: bool


ThingRespList = TypeAdapter(tuple[ThingResp, ...])
