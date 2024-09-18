from typing import Any

from msgspec import Struct, field

from HABApp.openhab.definitions import ThingStatusDetailEnum, ThingStatusEnum


class ChannelResp(Struct, kw_only=True):
    # ChannelDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/dto/ChannelDTO.java

    uid: str
    id: str
    channel_type: str | None = field(default=None, name='channelTypeUID')
    item_type: str | None = field(default=None, name='itemType')
    kind: str
    label: str = ''
    description: str = ''
    default_tags: list[str] = field(default=list, name='defaultTags')
    properties: dict[str, Any] = {}
    configuration: dict[str, Any] = {}
    auto_update_policy: str = field(default='', name='autoUpdatePolicy')

    # EnrichedChannelDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/thing/EnrichedChannelDTO.java
    linked_items: list[str] = field(name='linkedItems')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/ThingStatusInfo.java
class ThingStatusResp(Struct):
    status: ThingStatusEnum
    detail: ThingStatusDetailEnum = field(name='statusDetail')
    description: str | None = None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/firmware/dto/FirmwareStatusDTO.java
class FirmwareStatusResp(Struct):
    status: str
    updatable_version: str | None = field(default=None, name='updatableVersion')


class ThingResp(Struct, kw_only=True):
    # AbstractThingDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/dto/AbstractThingDTO.java
    label: str = ''
    bridge_uid: str | None = field(default=None, name='bridgeUID')
    configuration: dict[str, Any] = {}
    properties: dict[str, str] = {}
    uid: str = field(name='UID')
    thing_type: str = field(name='thingTypeUID')
    location: str = ''

    # EnrichedThingDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/thing/EnrichedThingDTO.java
    channels: list[ChannelResp] = []
    status: ThingStatusResp = field(name='statusInfo')
    firmware_status: FirmwareStatusResp | None = None
    editable: bool
