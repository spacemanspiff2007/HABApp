import dataclasses
from typing import Any, Dict

from pydantic import Field
from pydantic.dataclasses import dataclass

from .base import RestBase


@dataclass
class ItemChannelLinkDefinition(RestBase):
    item_name: str = Field(alias='itemName')
    channel_uid: str = Field(alias='channelUID')
    configuration: Dict[str, Any] = dataclasses.field(default_factory=dict)


class LinkNotFoundError(Exception):
    pass
