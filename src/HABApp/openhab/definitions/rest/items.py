from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StateOptionDefinition(BaseModel):
    value: str
    label: str | None = None


class CommandOptionDefinition(BaseModel):
    command: str
    label: str | None = None


class CommandDescriptionDefinition(BaseModel):
    command_options: list[CommandOptionDefinition] | None = Field(None, alias='commandOptions')


class StateDescriptionDefinition(BaseModel):
    minimum: int | float | None = None
    maximum: int | float | None = None
    step: int | float | None = None
    pattern: str | None = None
    read_only: bool | None = Field(None, alias='readOnly')
    options: list[StateOptionDefinition] | None = None


class GroupFunctionDefinition(BaseModel):
    name: str
    params: list[str] | None = None


class OpenhabItemDefinition(BaseModel):
    type: str
    name: str
    link: str
    state: Any
    label: str | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=list, alias='groupNames')
    members: list[OpenhabItemDefinition] = []
    transformed_state: str | None = Field(None, alias='transformedState')
    state_description: StateDescriptionDefinition | None = Field(None, alias='stateDescription')
    command_description: CommandDescriptionDefinition | None = Field(None, alias='commandDescription')
    metadata: dict[str, Any] = {}
    editable: bool = True

    # Group only fields
    group_type: str | None = Field(None, alias='groupType')
    group_function: GroupFunctionDefinition | None = Field(None, alias='function')


OpenhabItemDefinition.model_rebuild()
