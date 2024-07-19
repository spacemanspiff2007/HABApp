import importlib
import pkgutil
from dataclasses import dataclass
from inspect import getmembers
from types import ModuleType
from typing import Any, Iterable, List, Optional, Tuple, Type

import HABApp


def habapp_modules():
    modules: List[ModuleType] = []
    module_info = pkgutil.walk_packages(HABApp.__path__, HABApp.__name__ + '.')
    for package in sorted(module_info, key=lambda x: x.name):
        modules.append(importlib.import_module(package.name))

    return modules


@dataclass
class FoundObj:
    module_name: str
    obj: Any


def find_in_modules(objs: Optional[Iterable[Any]] = None,
                    instances: Optional[Tuple[Type[object], ...]] = None):

    assert objs or instances

    predicates = []
    if objs:
        def is_obj(x):
            for obj in objs:
                if obj is x:
                    return True
            return False
        predicates.append(is_obj)

    if instances:
        predicates.append(lambda x: isinstance(x, instances))

    ret: List[FoundObj] = []
    for module in habapp_modules():
        for name, obj in getmembers(module, predicate=lambda x: any(p(x) for p in predicates)):
            ret.append(FoundObj(name, obj))

    return ret
