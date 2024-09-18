from __future__ import annotations

from typing import Any

from msgspec import Struct, field


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/StateOption.java
class StateOptionResp(Struct):
    value: str
    label: str | None = None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/StateDescription.java
class StateDescriptionResp(Struct, kw_only=True):
    minimum: int | float | None = None
    maximum: int | float | None = None
    step: int | float | None = None
    pattern: str | None = None
    read_only: bool = field(name='readOnly')
    options: list[StateOptionResp]


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/CommandOption.java
class CommandOptionResp(Struct):
    command: str
    label: str | None = None


class CommandDescriptionResp(Struct):
    command_options: list[CommandOptionResp] = field(name='commandOptions')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/GroupFunctionDTO.java
class GroupFunctionResp(Struct):
    name: str
    params: list[str] = []


class ItemResp(Struct, kw_only=True):
    # ItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/ItemDTO.java
    type: str
    name: str
    label: str | None = None
    category: str | None = None
    tags: list[str]
    groups: list[str] = field(name='groupNames')

    # EnrichedItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/item/EnrichedItemDTO.java
    link: str | None = None
    state: str
    transformed_state: str | None = field(default=None, name='transformedState')
    state_description: StateDescriptionResp | None = field(default=None, name='stateDescription')
    unit: str | None = field(default=None, name='unitSymbol')
    command_description: CommandDescriptionResp | None = field(default=None, name='commandDescription')
    metadata: dict[str, Any] = {}
    editable: bool = True

    # EnrichedGroupItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/item/EnrichedGroupItemDTO.java
    members: list[ItemResp] = []
    group_type: str | None = field(default=None, name='groupType')
    group_function: GroupFunctionResp | None = field(default=None, name='function')


class ShortItemResp(Struct):
    type: str
    name: str
    state: str
