from typing import Any, Dict

from pydantic import Field

from .base import RestBase


class ItemChannelLinkDefinition(RestBase):
    editable: bool
    channel_uid: str = Field(alias='channelUID')
    configuration: Dict[str, Any] = {}
    item_name: str = Field(alias='itemName')


class LinkNotFoundError(Exception):
    pass
