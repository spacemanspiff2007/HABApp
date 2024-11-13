import re
import typing
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Annotated

from pydantic import AfterValidator, ConfigDict, Field, TypeAdapter, ValidationError, field_validator
from pydantic import BaseModel as _BaseModel

from HABApp.core.logger import HABAppError
from HABApp.openhab.connection.plugins.plugin_things.filters import ChannelFilter, ThingFilter
from HABApp.openhab.connection.plugins.plugin_things.str_builder import StrBuilder
from HABApp.openhab.definitions import ITEM_TYPES

from ._log import log


RE_VALID_NAME = re.compile(r'\w+')


@dataclass
class UserItem:
    type: str
    name: str
    label: str
    icon: str
    groups: list[str]
    tags: list[str]
    link: str | None
    metadata: dict[str, dict[str, str | int | float]]

    def get_oh_cfg(self) -> dict[str, str | dict | list]:
        ret = {}
        for k in self.__annotations__:
            if k in ('link', 'metadata'):
                continue

            v = self.__dict__[k]
            if k == 'icon':
                k = 'category'
            ret[k] = v
        return ret


class InvalidItemNameError(Exception):
    pass


class BaseModel(_BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra='forbid', validate_default=True, strict=True)


class MetadataCfg(BaseModel):
    value: str
    config: dict[str, typing.Any] = {}


def mk_str_builder(v: str) -> StrBuilder:
    return StrBuilder(v)


TypeStrBuilder = Annotated[str, AfterValidator(mk_str_builder)]


class UserItemCfg(BaseModel):
    type: str
    name: TypeStrBuilder
    label: TypeStrBuilder = ''
    icon: TypeStrBuilder = ''
    groups: list[TypeStrBuilder] = []
    tags: list[TypeStrBuilder] = []
    metadata: dict[str, MetadataCfg] | None = None

    @field_validator('type')
    def validate_item_type(cls, v):
        if v in ITEM_TYPES:
            return v
        try:
            return {k.lower(): k for k in ITEM_TYPES}[v.lower()]
        except KeyError:
            msg = f'Must be one of {", ".join(ITEM_TYPES)}'
            raise ValueError(msg) from None

    @field_validator('metadata', mode='before')
    def make_meta_cfg(cls, v):
        if not isinstance(v, dict):
            return v

        for key, val in v.items():
            if isinstance(val, str):
                v[key] = {'value': val}
        return v

    def get_item(self, context: dict) -> UserItem:
        v = {'link': None}
        for k in self.model_fields:
            val = self.__dict__[k]

            # type is const
            if k == 'type':
                v[k] = val
                continue

            # metadata is nested
            if k == 'metadata':
                v[k] = {k: v.model_dump() for k, v in val.items()} if val is not None else {}
                continue

            # resolve str wildcards
            if k in ('groups', 'tags'):
                v[k] = [s.get_str(context) for s in val]
                continue

            v[k] = val.get_str(context)

        # ensure a valid item name, otherwise the creation will definitely fail
        v['name'] = name = v['name'].replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace(' ', '_')
        if not RE_VALID_NAME.fullmatch(name):
            msg = f'"{name}" is not a valid name for an item!\n   (created for {context})'
            raise InvalidItemNameError(msg)
        return UserItem(**v)


class UserChannelCfg(BaseModel):
    filter: list[ChannelFilter]
    link_items: list[UserItemCfg] = Field(default_factory=list, alias='link items')

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_validator('filter', mode='before')
    def validate_filter(cls, v):
        return create_filters(ChannelFilter, v)

    def get_items(self, context: dict) -> Iterator[UserItem]:
        return map(lambda x: x.get_item(context), self.link_items)


class UserThingCfg(BaseModel):
    test: bool
    filter: list[ThingFilter]
    # order of the type hint matters: int, str!
    thing_config: dict[int | str, int | float | str | list[str]] = Field(alias='thing config',
                                                                                   default_factory=dict)
    create_items: list[UserItemCfg] = Field(alias='create items', default_factory=list)
    channels: list[UserChannelCfg] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @field_validator('filter', mode='before')
    def validate_filter(cls, v):
        return create_filters(ThingFilter, v)

    def get_items(self, context: dict) -> Iterator[UserItem]:
        return map(lambda x: x.get_item(context), self.create_items)


def create_filters(cls, v: list[dict[str, str]] | dict[str, str]):
    if isinstance(v, dict):
        v = [v]
    r = []
    for a in v:
        if not isinstance(a, dict):
            raise ValueError(f'Entry {a} is not a valid dict!')
        for key, regex in a.items():
            r.append(cls(key, regex))
    return r


def validate_cfg(_in, filename: str | None = None) -> list[UserThingCfg] | None:
    try:
        if isinstance(_in, list):
            return TypeAdapter(list[UserThingCfg]).validate_python(_in)
        else:
            return [UserThingCfg.model_validate(_in)]
    except ValidationError as e:
        log.error(f'Error while parsing "{filename}"')
        HABAppError(log).add_exception(e).dump()
        return None
