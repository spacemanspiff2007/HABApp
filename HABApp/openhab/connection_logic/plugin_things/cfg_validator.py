import re
from dataclasses import dataclass
from typing import Dict, List
from typing import Optional, Union, Iterator

from pydantic import BaseModel, validator, Field, parse_obj_as

from HABApp.openhab.connection_logic.plugin_things.filters import ThingFilter, ChannelFilter
from HABApp.openhab.connection_logic.plugin_things.str_builder import StrBuilder
from HABApp.openhab.definitions.definitions import ITEM_TYPES

RE_VALID_NAME = re.compile(r'\w+')


@dataclass
class UserItem:
    type: str
    name: str
    label: str
    icon: str
    groups: List[str]
    tags: List[str]
    link: Optional[str]

    def get_oh_cfg(self) -> Dict[str, Union[str, dict, list]]:
        ret = {}
        for k in self.__annotations__:
            if k == 'link':
                continue

            v = self.__dict__[k]
            if k == 'icon':
                k = 'category'
            ret[k] = v
        return ret


class UserItemCfg(BaseModel):
    type: str
    name: str
    label: str = ''
    icon: str = ''
    groups: List[str] = []
    tags: List[str] = []

    @validator('type', always=True)
    def validate_item_type(cls, v):
        if v in ITEM_TYPES:
            return v
        try:
            return {k.lower(): k for k in ITEM_TYPES}[v.lower()]
        except KeyError:
            raise ValueError(f'Must be one of {", ".join(ITEM_TYPES)}')

    @validator('name', 'label', 'icon', 'groups', 'tags', each_item=True, always=True)
    def validate_make_str_builder(cls, v):
        return StrBuilder(v)

    def get_item(self, context: dict) -> UserItem:
        v = {'link': None}
        for k in self.__fields__:
            val = self.__dict__[k]
            if k == 'type':
                v[k] = val
                continue
            if k in ('groups', 'tags'):
                v[k] = [s.get_str(context) for s in val]
                continue
            v[k] = val.get_str(context)

        # ensure a valid item name, otherwise the creation will definitely fail
        v['name'] = name = v['name'].replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace(' ', '_')
        if not RE_VALID_NAME.fullmatch(name):
            raise ValueError(f'"{name}" is not a valid name for an item!')
        return UserItem(**v)


class UserChannelCfg(BaseModel):
    filter: List[ChannelFilter]
    link_item: List[UserItemCfg] = Field(default_factory=list, alias='link item')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    @validator('filter', pre=True, always=True)
    def validate_filter(cls, v):
        return create_filters(ChannelFilter, v)

    def get_items(self, context: dict) -> Iterator[UserItem]:
        return map(lambda x: x.get_item(context), self.link_item)


class UserThingCfg(BaseModel):
    test: bool
    filter: List[ThingFilter]
    # order of the type hint matters: int, str!
    thing_config: Dict[Union[int, str], Union[int, float, str]] = Field(alias='thing config')
    create_item: List[UserItemCfg] = Field(alias='create item')
    channels: List[UserChannelCfg]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    @validator('filter', pre=True, always=True)
    def validate_filter(cls, v):
        return create_filters(ThingFilter, v)

    def get_items(self, context: dict) -> Iterator[UserItem]:
        return map(lambda x: x.get_item(context), self.create_item)


def create_filters(cls, v: Union[List[Dict[str, str]], Dict[str, str]]):
    if isinstance(v, dict):
        v = [v]
    r = []
    for a in v:
        for key, regex in a.items():
            r.append(cls(key, regex))
    return r


def validate_cfg(_in) -> List[UserThingCfg]:
    if isinstance(_in, list):
        return parse_obj_as(List[UserThingCfg], _in)
    else:
        return [parse_obj_as(UserThingCfg, _in)]
