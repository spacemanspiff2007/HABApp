from typing import Any, Optional, Union, List

from pydantic import BaseModel, Field


class StateOptionDefinition(BaseModel):
    value: str
    label: Optional[str] = None


class CommandOptionDefinition(BaseModel):
    command: str
    label: Optional[str] = None


class CommandDescriptionDefinition(BaseModel):
    command_options: Optional[List[CommandOptionDefinition]] = Field(None, alias='commandOptions')


class StateDescriptionDefinition(BaseModel):
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    read_only: Optional[bool] = Field(None, alias='readOnly')
    options: Optional[List[StateOptionDefinition]] = None


class GroupFunctionDefinition(BaseModel):
    name: str
    params: Optional[List[str]] = None


class OpenhabItemDefinition(BaseModel):
    type: str
    name: str
    link: str
    state: Any
    label: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list, alias='groupNames')
    members: List['OpenhabItemDefinition'] = []
    transformed_state: Optional[str] = Field(None, alias='transformedState')
    state_description: Optional[StateDescriptionDefinition] = Field(None, alias='stateDescription')
    command_description: Optional[CommandDescriptionDefinition] = Field(None, alias='commandDescription')
    metadata: dict[str, Any] = {}
    editable: bool = True

    # Group only fields
    group_type: Optional[str] = Field(None, alias='groupType')
    group_function: Optional[GroupFunctionDefinition] = Field(None, alias='function')


OpenhabItemDefinition.model_rebuild()
