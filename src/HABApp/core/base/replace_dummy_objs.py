from inspect import getmembers
from types import ModuleType
from typing import List, Tuple, Any, Optional


class ReplacedObjects:
    def __init__(self):
        self.replaced_objs: List[Tuple[ModuleType, str, Any]] = []

    def add(self, module: ModuleType, name: str, obj: Any):
        self.replaced_objs.append((module, name, obj))

    def restore(self):
        for module, name, obj in self.replaced_objs:
            setattr(module, name, obj)


def replace_dummy_objs(module: ModuleType, to_replace, replacement,
                       replaced_objs: Optional[ReplacedObjects] = None, already_processed=None, ) -> ReplacedObjects:
    """Replace all dummy objects with the real thing"""
    assert isinstance(module, ModuleType)

    if already_processed is None:
        already_processed = set()
    if replaced_objs is None:
        replaced_objs = ReplacedObjects()

    module_replace = getmembers(module, lambda x: x is to_replace)              # type: List[Tuple[str, Any]]
    sub_modules = getmembers(module, lambda x: isinstance(x, ModuleType))   # type: List[Tuple[str, ModuleType]]

    for name, subs in module_replace:
        replaced_objs.add(module, name, getattr(module, name))
        setattr(module, name, replacement)

    for _, subs in sub_modules:
        name = subs.__name__
        if name in already_processed or not name.startswith('HABApp'):
            continue
        already_processed.add(name)

        # print(name)
        replace_dummy_objs(subs, to_replace=to_replace, replacement=replacement, already_processed=already_processed)

    return replaced_objs
