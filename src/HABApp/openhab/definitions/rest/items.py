from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class StateOptionDefinition(BaseModel):
    value: str
    label: Optional[str] = None


class CommandOptionDefinition(BaseModel):
    command: str
    label: Optional[str] = None


class CommandDescriptionDefinition(BaseModel):
    command_options: Optional[List[CommandOptionDefinition]] = Field(alias='commandOptions')


class StateDescriptionDefinition(BaseModel):
    minimum: Optional[Union[int, float]]
    maximum: Optional[Union[int, float]]
    step: Optional[Union[int, float]]
    pattern: Optional[str]
    read_only: Optional[bool] = Field(alias='readOnly')
    options: Optional[List[StateOptionDefinition]]


class GroupFunctionDefinition(BaseModel):
    name: str
    params: Optional[List[str]]


class OpenhabItemDefinition(BaseModel):
    type: str
    name: str
    label: Optional[str]
    category: Optional[str]
    tags: List[str]
    link: str
    state: Any
    groups: List[str] = Field(alias='groupNames')
    members: List['OpenhabItemDefinition'] = []
    transformed_state: Optional[str] = Field(alias='transformedState')
    state_description: Optional[StateDescriptionDefinition] = Field(alias='stateDescription')
    command_description: Optional[CommandDescriptionDefinition] = Field(alias='commandDescription')
    metadata: Dict[str, Any] = {}
    editable: bool = True

    # Group only fields
    group_type: Optional[str] = Field(alias='groupType')
    group_function: Optional[GroupFunctionDefinition] = Field(alias='function')


OpenhabItemDefinition.update_forward_refs()
