from __future__ import annotations

from typing import Generic, TypeVar, Literal, Union, Iterator, Tuple

from HABApp.core.const.const import PYTHON_310

if PYTHON_310:
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


T = TypeVar('T')

T_PRIO: TypeAlias = Union[Literal['first', 'last'], int]
T_ENTRY: TypeAlias = Tuple[T_PRIO, T]


def sort_func(obj: T_ENTRY):
    prio = {'first': 0, 'last': 2}
    key = obj[0]
    assert isinstance(key, int) or key in prio
    return prio.get(key, 1), key


class PriorityList(Generic[T]):
    def __init__(self):
        self._objs: list[T_ENTRY] = []

    def append(self, obj: T, priority: T_PRIO):
        for o in self._objs:
            assert o[0] != priority, priority
        self._objs.append((priority, obj))
        self._objs.sort(key=sort_func)

    def remove(self, obj: T):
        for i, (_, existing) in self._objs:
            if existing is obj:
                self._objs.pop(i)
                return None

    def __iter__(self) -> Iterator[T]:
        for p, o in self._objs:
            yield o

    def reversed(self) -> Iterator[T]:
        for p, o in reversed(self._objs):
            yield o

    def __repr__(self):
        return f'<{self.__class__.__name__} {[o for o in self]}>'
