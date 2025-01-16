from typing import Any, Final

from typing_extensions import Self

from HABApp.openhab.definitions.types import OpenHABDataType


class ValueToOh:
    __slots__ = ('_name', '_types')

    def __init__(self, name: str, *types: type[OpenHABDataType]) -> None:
        self._name: Final = name
        self._types: Final = tuple(self._check_type(t, check_existing=False) for t in types)

        if len(set(self._types)) != len(self._types):
            msg = 'Duplicate entries in types'
            raise ValueError(msg)

    def _check_type(self, other: Any, *, check_existing: bool = True) -> type[OpenHABDataType]:
        if not issubclass(other, OpenHABDataType):
            msg = f'Expected OpenHABType, got {type(other)}'
            raise TypeError(msg)
        if check_existing and other in self._types:
            msg = f'{other.__name__} already in {self._name:s}'
            raise ValueError(msg)
        return other

    def add_type(self, name: str, other: Any) -> Self:
        if other is None:
            return ValueToOh(*self._types)

        if isinstance(other, tuple):
            return ValueToOh(*self._types, *[self._check_type(o) for o in other])

        return ValueToOh(name, *self._types, self._check_type(other))

    def replace_type(self, existing: type[OpenHABDataType], new: type[OpenHABDataType]) -> Self:
        existing = self._check_type(existing, check_existing=False)
        new = self._check_type(new)

        if existing not in self._types:
            return self

        types = list(self._types)
        types[types.index(existing)] = new
        return self.__class__(self._name, *types)

    def to_oh_str(self, value: Any) -> str:
        for t in self._types:
            if (r := t.to_oh_str(value)) is not None:
                return r

        msg = f"Invalid value: '{value}' ({type(value)}) for {self._name:s}"
        raise ValueError(msg)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}{self._name:s}({", ".join(t.__name__ for t in self._types)})'
