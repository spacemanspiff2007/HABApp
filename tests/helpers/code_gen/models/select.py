import asyncio
import re
import typing
from re import Pattern
from typing import Any, Self, override

import pydantic
import pydantic_core
import whenever
from pydantic import PrivateAttr

from tests.helpers.code_gen.module_context import ModuleContext

from ._base import BaseModel, BaseOperation, VarType


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

    def model_post_init(self, context: Any) -> Self:  # noqa: ARG002

        include = self.include if isinstance(self.include, list) else [self.include]
        exclude = []
        if self.exclude is not None:
            exclude = self.exclude if isinstance(self.exclude, list) else [self.exclude]

        self._pattern_include = tuple(re.compile(r, re.IGNORECASE) for r in include)
        self._pattern_exclude = tuple(re.compile(r, re.IGNORECASE) for r in exclude)
        return self

    @override
    def select_objects(self, module: ModuleContext) -> dict[str, type]:
        ret: dict[str, type] = {}

        module_objs = module.get_objects()
        for name, obj in module_objs.items():
            if self.exclude_default:
                if name.endswith(('BaseModel', 'Base', 'Mixin')):
                    continue
                if ((obj_module := getattr(obj, '__module__', None)) is not None and
                        obj_module in (pydantic, pydantic_core, typing, whenever, asyncio)):
                    continue

            for p in self._pattern_include:
                if p.search(name):
                    break
            else:
                continue

            for p in self._pattern_exclude:
                if p.search(name):
                    break
            else:
                ret[name] = obj

        if not ret:
            msg = f'Nothing found for {self}'
            raise ValueError(msg)

        return module.set_var(self.name, ret)


class SelectOperation(BaseOperation):
    select: SelectModuleObjs

    @override
    def execute(self, module: ModuleContext) -> str:
        self.select.select_objects(module)
        return ''


class SelectModuleObjsNoDefault(SelectModuleObjs):
    exclude_default: bool = False


SelectInputType = SelectVariable | SelectModuleObjs
SelectInputTypeNoDefault = SelectVariable | SelectModuleObjsNoDefault
