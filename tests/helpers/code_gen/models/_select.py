import asyncio
import enum
import inspect
import re
import typing
from re import Pattern
from typing import Annotated, Any, get_args, get_origin, override

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

    @override
    def select_objects(self, module: ModuleContext) -> dict[str, type]:
        ret: dict[str, type] = {}

        module_objs = module.get_objects()
        for name, obj in module_objs.items():

            if self.exclude_default:
                if name.endswith(('BaseModel', 'Base', 'Mixin')):
                    continue

                # unpack Annotated, otherwise it points to the typing module and we ignore it
                _obj = obj
                while get_origin(_obj) is Annotated:
                    _obj = get_args(_obj)[0]

                if ((obj_module := inspect.getmodule(_obj)) is not None and
                        obj_module in (pydantic, pydantic_core, typing, whenever, asyncio, enum)):
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
