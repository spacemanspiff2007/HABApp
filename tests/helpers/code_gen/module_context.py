from types import ModuleType
from typing import Any, Final


class ModuleContext:

    def __init__(self, module: ModuleType) -> None:
        self._module: Final = module
        self._vars: Final[dict[str, dict[str, type]]] = {}

    def set_var(self, name: str | None, value: dict[str, type]) -> dict[str, type]:
        if name is None:
            return value
        if not isinstance(name, str):
            raise TypeError()

        self._vars[name.lower()] = value
        return value

    def get_var(self, name: str) -> dict[str, type]:
        return self._vars[name.lower()]

    def get_objects(self) -> dict[str, Any]:
        ret = {}

        for name in dir(self._module):
            if name.startswith('__'):
                continue
            obj = getattr(self._module, name)
            ret[name] = obj

        return ret

    def __repr__(self) -> str:
        return f'{self.__class__.__name__:s}({self._module.__name__})'
