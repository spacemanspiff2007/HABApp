from typing import Any, Dict

from pydantic import Field

from .base import RestBase


class ItemChannelLinkDefinition(RestBase):
    item_name: str = Field(alias='itemName')
    channel_uid: str = Field(alias='channelUID')
    configuration: Dict[str, Any] = {}

    # This field is OH3 only
    # Todo: Remove this comment once we go OH3
    editable: bool = False


class LinkNotFoundError(Exception):
    pass
