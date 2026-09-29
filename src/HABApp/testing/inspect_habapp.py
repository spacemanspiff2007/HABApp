import functools
import importlib
import pkgutil
from collections.abc import Callable
from inspect import getmembers
from types import ModuleType
from typing import Any, Final

import HABApp


@functools.cache
def habapp_modules() -> tuple[ModuleType, ...]:

    modules: Final[list[ModuleType]] = []
    module_info: Final = pkgutil.walk_packages(HABApp.__path__, HABApp.__name__ + '.')

    for package in sorted(module_info, key=lambda x: x.name):
        modules.append(importlib.import_module(package.name))

    return tuple(modules)


def find_in_modules(predicate: Callable[[Any], bool]) -> list[tuple[ModuleType, str, Any]]:
    ret: list[tuple[ModuleType, str, Any]] = []
    for module in habapp_modules():
        for name, obj in getmembers(module, predicate=predicate):
            ret.append((module, name, obj))

    if not ret:
        msg = f'No objects found in HABApp modules matching predicate {predicate!r}'
        raise ValueError(msg)

    return ret
