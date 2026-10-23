from typing import Any, override

from HABApp.core.internals import EventFilterBase


class EventFilterBaseGroup(EventFilterBase):
    __slots__ = ('filters', )

    def __init__(self, *args: EventFilterBase) -> None:
        self.filters: tuple[EventFilterBase, ...] = args

    @override
    def trigger(self, event: Any) -> bool:
        raise NotImplementedError()

    @override
    def describe(self) -> str:
        raise NotImplementedError()


class OrFilterGroup(EventFilterBaseGroup):
    """Only one child filter has to match"""

    __slots__ = ()

    @override
    def trigger(self, event: Any) -> bool:
        return any(f.trigger(event) for f in self.filters)

    @override
    def describe(self) -> str:
        objs = [f.describe() for f in self.filters]
        return f'({" or ".join(objs)})'


class AndFilterGroup(EventFilterBaseGroup):
    """All child filters have to match"""

    __slots__ = ()

    @override
    def trigger(self, event: Any) -> bool:
        return all(f.trigger(event) for f in self.filters)

    @override
    def describe(self) -> str:
        objs = [f.describe() for f in self.filters]
        return f'({" and ".join(objs)})'
