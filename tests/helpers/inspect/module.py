import importlib
import sys
import types
import typing
from collections.abc import Callable, Iterable
from inspect import getmembers, isclass
from typing import Final


def get_module_classes(module: str | types.ModuleType, /, exclude: Iterable[str | type] | None = None, *,
                       include_imported: bool = True,
                       subclass: type | tuple[type, ...] | None = None, include_subclass: bool = True):

    if isinstance(module, str):
        importlib.import_module(module)
        module_obj: Final = sys.modules[module]
    else:
        module_obj: Final = module

    module_name = module_obj.__name__

    filters: Final[list[Callable[[type], bool]]] = [
        isclass,

        # exclude typing classes by default (e.g. Any, Union)
        lambda x: x not in tuple(getattr(typing, name) for name in typing.__all__),
    ]

    if not include_imported:
        filters.append(lambda x: x.__module__ == module_name)

    if exclude is not None:
        for exclude_obj in exclude:
            if isinstance(exclude_obj, str):
                filters.append(lambda x, obj=exclude_obj: x.__name__ != obj)
            else:
                filters.append(lambda x, obj=exclude_obj: x is not obj)

    if subclass is not None:
        subclasses: Final[tuple[type, ...]] = subclass if isinstance(subclass, tuple) else (subclass,)

        filters.append(lambda x: issubclass(x, subclasses))

        # Ensure that the class is not the subclass
        if not include_subclass:
            filters.append(lambda x: all(x is not cls_obj for cls_obj in subclasses))

    return dict(getmembers(
        module_obj,
        lambda x: all(f(x) for f in filters)
    ))
