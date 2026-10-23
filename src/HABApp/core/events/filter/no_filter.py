from typing import Any, override

from HABApp.core.internals import EventFilterBase


class NoEventFilter(EventFilterBase):
    """Triggers on all events"""

    __slots__ = ()

    @override
    def trigger(self, event: Any) -> bool:
        return True

    @override
    def describe(self) -> str:
        return f'{self.__class__.__name__}()'
