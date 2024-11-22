from typing import Any

from pydantic import BaseModel, Field, TypeAdapter


class ItemChannelLinkResp(BaseModel):
    # AbstractLinkDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/link/dto/AbstractLinkDTO.java
    item: str = Field(alias='itemName')

    # ItemChannelLinkDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/link/dto/ItemChannelLinkDTO.java
    channel: str = Field(alias='channelUID')
    configuration: dict[str, Any] = {}

    # EnrichedItemChannelLinkDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/link/EnrichedItemChannelLinkDTO.java
    editable: bool


ItemChannelLinkRespList = TypeAdapter(tuple[ItemChannelLinkResp, ...])
