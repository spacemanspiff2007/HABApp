from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class OpenhabThingChannelDefinition(BaseModel):
    linkedItems: Optional[List[str]]
    uid: Optional[str]
    id: Optional[str]
    channelTypeUID: Optional[str]
    itemType: Optional[str]
    kind: Optional[str]
    label: Optional[str]
    description: Optional[str]
    defaultTags: Optional[List[str]]
    properties: Optional[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]]


class OpenhabThingStatus(BaseModel):
    status: str
    detail: str = Field(..., alias='statusDetail')
    description: Optional[str] = None


class OpenhabThingDefinition(BaseModel):
    channels: Optional[List[OpenhabThingChannelDefinition]]
    location: Optional[str]
    firmwareStatus: Optional[Dict[str, str]]
    editable: Optional[bool]

    # Field is actually optional but we set this to an empty str
    label: str = ''

    # These are mandatory fields
    status: OpenhabThingStatus = Field(..., alias='statusInfo')
    uid: str = Field(..., alias='UID')
    thing_type: str = Field(..., alias='thingTypeUID')
    bridge_uid: Optional[str] = Field(None, alias='bridgeUID')

    configuration: Dict[str, Any]
    properties: Dict[str, Any]

    @validator('label')
    def none_to_empty_str(cls, v):
        if v is None:
            return ''
        return v
