from typing import Any, Dict

from pydantic import Field

from .base import RestBase


class ItemChannelLinkDefinition(RestBase):
    item_name: str = Field(alias='itemName')
    channel_uid: str = Field(alias='channelUID')
    configuration: Dict[str, Any] = {}


class LinkNotFoundError(Exception):
    pass
