from typing import Any, Dict, List, Optional, Union

from msgspec import Struct, field


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/StateOption.java
class StateOptionResp(Struct):
    value: str
    label: Optional[str] = None


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/StateDescription.java
class StateDescriptionResp(Struct, kw_only=True):
    minimum: Union[int, float, None] = None
    maximum: Union[int, float, None] = None
    step: Union[int, float, None] = None
    pattern: Optional[str] = None
    read_only: bool = field(name='readOnly')
    options: List[StateOptionResp]


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/types/CommandOption.java
class CommandOptionResp(Struct):
    command: str
    label: Optional[str] = None


class CommandDescriptionResp(Struct):
    command_options: List[CommandOptionResp] = field(name='commandOptions')


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/GroupFunctionDTO.java
class GroupFunctionResp(Struct):
    name: str
    params: List[str] = []


class ItemResp(Struct, kw_only=True):
    # ItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/items/dto/ItemDTO.java
    type: str
    name: str
    label: Optional[str] = None
    category: Optional[str] = None
    tags: List[str]
    groups: List[str] = field(name='groupNames')

    # EnrichedItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/item/EnrichedItemDTO.java
    link: Optional[str] = None
    state: str
    transformed_state: Optional[str] = field(default=None, name='transformedState')
    state_description: Optional[StateDescriptionResp] = field(default=None, name='stateDescription')
    unit: Optional[str] = field(default=None, name='unitSymbol')
    command_description: Optional[CommandDescriptionResp] = field(default=None, name='commandDescription')
    metadata: Dict[str, Any] = {}
    editable: bool = True

    # EnrichedGroupItemDTO
    # https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core.io.rest.core/src/main/java/org/openhab/core/io/rest/core/item/EnrichedGroupItemDTO.java
    members: List['ItemResp'] = []
    group_type: Optional[str] = field(default=None, name='groupType')
    group_function: Optional[GroupFunctionResp] = field(default=None, name='function')


class ShortItemResp(Struct):
    type: str
    name: str
    state: str
