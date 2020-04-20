from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class StateDescriptionDefinition(BaseModel):
    minimum: Optional[Union[int, float]]
    maximum: Optional[Union[int, float]]
    step: Optional[Union[int, float]]
    pattern: Optional[str]
    read_only: Optional[bool] = Field(alias='readOnly')
    options: Dict[str, str] = {}


class OpenhabItemDefinition(BaseModel):
    type: str
    name: str
    label: str
    link: str
    state: Any
    category: Optional[str]
    editable: bool = True
    tags: List[str]
    groups: List[str] = Field(alias='groupNames')
    members: List['OpenhabItemDefinition']
    transformed_state: Optional[str] = Field(alias='transformedState')


OpenhabItemDefinition.update_forward_refs()
