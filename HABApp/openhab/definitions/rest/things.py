from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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


class OpenhabThingDefinition(BaseModel):
    label: Optional[str]
    bridgeUID: Optional[str]
    configuration: Dict[str, Any]
    properties: Dict[str, Any]
    UID: Optional[str]
    thingTypeUID: Optional[str]
    channels: Optional[List[OpenhabThingChannelDefinition]]
    location: Optional[str]
    statusInfo: Optional[Dict[str, str]]
    firmwareStatus: Optional[Dict[str, str]]
    editable: Optional[bool]
