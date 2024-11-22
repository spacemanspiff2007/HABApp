import importlib
import pkgutil
from dataclasses import dataclass
from inspect import getmembers
from typing import TYPE_CHECKING, Any

import HABApp


if TYPE_CHECKING:
    from types import ModuleType


def habapp_modules():
    modules: list[ModuleType] = []
    module_info = pkgutil.walk_packages(HABApp.__path__, HABApp.__name__ + '.')
    for package in sorted(module_info, key=lambda x: x.name):
        modules.append(importlib.import_module(package.name))

    return modules


@dataclass
class FoundObj:
    module_name: str
    obj: Any


def find_in_modules(instances: tuple[type[object], ...] | None = None,
                    subclasses: tuple[type[object], ...] | None = None) -> list[FoundObj]:
    predicates = []

    if instances:
        predicates.append(lambda x: isinstance(x, instances))
    if subclasses:
        predicates.append(lambda x: issubclass(x, subclasses))

    ret: list[FoundObj] = []
    for module in habapp_modules():
        for name, obj in getmembers(module, predicate=lambda x: any(p(x) for p in predicates)):
            ret.append(FoundObj(name, obj))

    assert ret
    return ret
