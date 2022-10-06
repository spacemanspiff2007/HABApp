from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field, validator


class OpenhabThingChannelDefinition(BaseModel):
    uid: str
    id: str
    channel_type: str = Field(..., alias='channelTypeUID')
    kind: str

    label: str = ''
    description: str = ''
    item_type: Optional[str] = Field(None, alias='itemType')

    linked_items: Tuple[str, ...] = Field(default_factory=tuple, alias='linkedItems')
    default_tags: Tuple[str, ...] = Field(default_factory=tuple, alias='defaultTags')

    properties: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)


class OpenhabThingStatus(BaseModel):
    status: str
    detail: str = Field(..., alias='statusDetail')
    description: Optional[str] = None

    @validator('detail')
    def _parse_detail(cls, v):
        return '' if v == 'NONE' else v


class OpenhabThingDefinition(BaseModel):
    # These are mandatory fields
    editable: bool
    status: OpenhabThingStatus = Field(..., alias='statusInfo')
    thing_type: str = Field(..., alias='thingTypeUID')
    uid: str = Field(..., alias='UID')

    # These fields are optional, but we want to have a value set
    # because it simplifies the thing handling a lot
    bridge_uid: Optional[str] = Field(None, alias='bridgeUID')
    label: str = ''
    location: str = ''

    # Containers should always have a default, so it's easy to iterate over them
    channels: Tuple[OpenhabThingChannelDefinition, ...] = Field(default_factory=tuple)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    firmwareStatus: Dict[str, str] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)
