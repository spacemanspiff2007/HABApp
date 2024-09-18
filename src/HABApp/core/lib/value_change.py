from __future__ import annotations

from typing import Generic, TypeVar

from HABApp.core.const.const import MISSING, _MissingType


T = TypeVar('T')


class ValueChange(Generic[T]):
    __slots__ = ('_value', 'changed')

    def __init__(self) -> None:
        self._value: T | _MissingType = MISSING
        self.changed: bool = False

    def set_value(self, value: T):
        current = self._value

        if value is MISSING and current is MISSING:
            self.changed = False
            return self

        if value is MISSING and current is not MISSING or value is not MISSING and current is MISSING:
            self._value = value
            self.changed = True
            return self

        if value != current:
            self._value = value
            self.changed = True
            return self

        self.changed = False
        return self

    def set_missing(self):
        self.set_value(MISSING)
        return self

    @property
    def is_missing(self) -> bool:
        return self._value is MISSING

    @property
    def value(self) -> T:
        if self._value is MISSING:
            raise ValueError()
        return self._value

    def __repr__(self) -> str:
        now = self._value if self._value is not MISSING else repr(MISSING)
        return f'<{self.__class__.__name__} value: {now} changed: {self.changed}>'
