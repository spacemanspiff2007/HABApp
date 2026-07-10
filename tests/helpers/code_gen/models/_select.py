import asyncio
import collections
import enum
import inspect
import re
import typing
from re import Pattern
from types import ModuleType, UnionType
from typing import Annotated, Any, Union, get_args, get_origin, override

import pydantic
import pydantic_core
import whenever
from pydantic import PrivateAttr

from tests.helpers.code_gen.models._base import BaseModel, VarType
from tests.helpers.code_gen.module_context import ModuleContext


class _SelectBaseModel(BaseModel):

    def select_objects(self, module: ModuleContext) -> dict[str, type]:
        raise NotImplementedError()


class SelectVariable(_SelectBaseModel):
    name: VarType

    @override
    def select_objects(self, module: ModuleContext) -> dict[str, type]:
        return module.get_var(self.name)


class SelectModuleObjs(_SelectBaseModel):
    name: VarType | None = None
    include: str | list[str]
    exclude: str | list[str] | None = None
    exclude_default: bool = True
    exclude_foreign: bool = False

    _pattern_include: tuple[Pattern, ...] = PrivateAttr()
    _pattern_exclude: tuple[Pattern, ...] = PrivateAttr()

    def model_post_init(self, context: Any) -> None:  # noqa: ARG002

        include = self.include if isinstance(self.include, list) else [self.include]
        exclude = []
        if self.exclude is not None:
            exclude = self.exclude if isinstance(self.exclude, list) else [self.exclude]

        self._pattern_include = tuple(re.compile(r, re.IGNORECASE) for r in include)
        self._pattern_exclude = tuple(re.compile(r, re.IGNORECASE) for r in exclude)
        return None

    def _name_is_included(self, name: str) -> bool:
        if not (pattern := self._pattern_include):
            return False
        return any(p.search(name) for p in pattern)

    def _name_is_excluded(self, name: str) -> bool:
        if not (pattern := self._pattern_exclude):
            return False
        return any(p.search(name) for p in pattern)

    def _is_foreign_excluded(self, name: str, obj: Any, this_module: ModuleType) -> bool:
        if not self.exclude_foreign:
            return False

        return (obj_module := inspect.getmodule(obj)) is not None and obj_module is not this_module

    def _is_default_excluded(self, name: str, obj: Any) -> bool:
        if not self.exclude_default:
            return False

        if name.endswith(('BaseModel', 'Base', 'Mixin')):
            return True

        # unpack Annotated and Union, otherwise it points to the typing module and we ignore it
        while True:
            if (origin := get_origin(obj)) is Annotated:
                obj = get_args(obj)[0]
                continue

            # if it's a union we don't ignore it
            if origin in (Union, UnionType) or isinstance(obj, UnionType):
                return False

            break

        return (obj_module := inspect.getmodule(obj)) is not None and obj_module in (
            pydantic,
            pydantic_core,
            typing,
            whenever,
            asyncio,
            enum,
            collections.abc,
        )

    @override
    def select_objects(self, module: ModuleContext) -> dict[str, type]:
        ret: dict[str, type] = {}

        module_objs = module.get_objects()
        for name, obj in module_objs.items():
            if self._is_default_excluded(name, obj):
                continue

            if self._is_foreign_excluded(name, obj, module._module):
                continue

            if not self._name_is_included(name):
                continue

            if self._name_is_excluded(name):
                continue

            ret[name] = obj

        if not ret:
            msg = f'Nothing found for {self}'
            raise ValueError(msg)

        return module.set_var(self.name, ret)


class SelectModuleObjsWithDefault(SelectModuleObjs):
    exclude_default: bool = False


SelectInputType = SelectVariable | SelectModuleObjs
SelectInputTypeWithDefault = SelectVariable | SelectModuleObjsWithDefault
