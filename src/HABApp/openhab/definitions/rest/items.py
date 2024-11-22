from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, TypeAdapter


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/StateOption.java
class StateOptionResp(BaseModel):
    value: str
    label: str | None = None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/StateDescription.java
class StateDescriptionResp(BaseModel):
    minimum: int | float | None = None
    maximum: int | float | None = None
    step: int | float | None = None
    pattern: str | None = None
    read_only: bool = Field(alias='readOnly')
    options: tuple[StateOptionResp, ...]


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/CommandOption.java
class CommandOptionResp(BaseModel):
    command: str
    label: str | None = None


class CommandDescriptionResp(BaseModel):
    command_options: tuple[CommandOptionResp, ...] = Field(alias='commandOptions')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/GroupFunctionDTO.java
class GroupFunctionResp(BaseModel):
    name: str
    params: tuple[str, ...] = ()


class ItemResp(BaseModel):
    # ItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/ItemDTO.java
    type: str
    name: str
    label: str | None = None
    category: str | None = None
    tags: tuple[str, ...]
    groups: tuple[str, ...] = Field(alias='groupNames')

    # EnrichedItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/item/EnrichedItemDTO.java
    link: str | None = None
    state: str
    transformed_state: str | None = Field(default=None, alias='transformedState')
    state_description: StateDescriptionResp | None = Field(default=None, alias='stateDescription')
    unit: str | None = Field(default=None, alias='unitSymbol')
    command_description: CommandDescriptionResp | None = Field(default=None, alias='commandDescription')
    metadata: dict[str, Any] = {}
    editable: bool = True

    # EnrichedGroupItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/item/EnrichedGroupItemDTO.java
    members: tuple[ItemResp, ...] = ()
    group_type: str | None = Field(default=None, alias='groupType')
    group_function: GroupFunctionResp | None = Field(default=None, alias='function')


ItemRespList = TypeAdapter(tuple[ItemResp, ...])


class ShortItemResp(BaseModel):
    type: str
    name: str
    state: str


ShortItemRespList = TypeAdapter(tuple[ShortItemResp, ...])
