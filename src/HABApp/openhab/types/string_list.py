from __future__ import annotations

from typing_extensions import Self


class StringList(tuple[str, ...]):
    """A frozen list where all entries are of type str"""

    __slots__ = ()

    def __new__(cls, iterable: tuple[str, ...] | list[str]) -> Self:
        for v in iterable:
            if not isinstance(v, str):
                msg = f'Expected str, got {type(v)} for {cls.__name__}'
                raise TypeError(msg)
        return super().__new__(cls, iterable)

    def __eq__(self, other: tuple[str, ...] | list[str]) -> bool:
        if isinstance(other, tuple):
            return super().__eq__(other)
        if isinstance(other, list):
            return super().__eq__(tuple(other))
        return NotImplemented

    def __ne__(self, other: tuple[str, ...] | list[str]) -> bool:
        if isinstance(other, tuple):
            return super().__ne__(other)
        if isinstance(other, list):
            return super().__ne__(tuple(other))
        return NotImplemented
