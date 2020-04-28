from typing import Dict, Any

from pydantic import BaseModel, Field


class ItemChannelLinkDefinition(BaseModel):
    item_name: str = Field(alias='itemName')
    channel_uid: str = Field(alias='channelUID')
    configuration: Dict[str, Any] = {}


class LinkNotFoundError(Exception):
    pass
