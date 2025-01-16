import importlib
import inspect
import sys
import types
import typing
from collections.abc import Callable, Iterable


def get_module_classes(module: str | types.ModuleType, /, exclude: Iterable[str | type] | None = None,
                       include_imported=True,
                       subclass: None | type | tuple[type, ...] = None, include_subclass=True):

    if isinstance(module, str):
        importlib.import_module(module)
        module_obj = sys.modules[module]
    else:
        module_obj = module

    module_name = module_obj.__name__

    filters: list[Callable[[type], bool]] = [
        lambda x: inspect.isclass(x),

        # exclude typing classes by default (e.g. Any, Union)
        lambda x: x not in [getattr(typing, name) for name in typing.__all__],
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
        filters.append(lambda x: issubclass(x, subclass))

        # Ensure that the class is not the subclass
        if not include_subclass:
            sub_cmp = subclass if isinstance(subclass, tuple) else tuple([subclass])
            filters.append(lambda x: all(map(lambda cls_obj: x is not cls_obj, sub_cmp)))

    return dict(inspect.getmembers(
        module_obj,
        lambda x: all(f(x) for f in filters)
    ))
