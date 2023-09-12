from typing import Any, Dict

from msgspec import Struct, field


class ItemChannelLinkResp(Struct, kw_only=True):
    # AbstractLinkDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/link/dto/AbstractLinkDTO.java
    item: str = field(name='itemName')

    # ItemChannelLinkDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.thing/src/main/java/org/openhab/core/thing/link/dto/ItemChannelLinkDTO.java
    channel: str = field(name='channelUID')
    configuration: Dict[str, Any] = {}

    # EnrichedItemChannelLinkDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/link/EnrichedItemChannelLinkDTO.java
    editable: bool
