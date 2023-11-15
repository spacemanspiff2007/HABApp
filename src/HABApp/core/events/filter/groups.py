from typing import Any, Tuple

from HABApp.core.internals import EventFilterBase, HINT_EVENT_FILTER_OBJ


class EventFilterBaseGroup(EventFilterBase):
    def __init__(self, *args: HINT_EVENT_FILTER_OBJ):
        self.filters: Tuple[HINT_EVENT_FILTER_OBJ, ...] = args

    def trigger(self, event) -> bool:
        raise NotImplementedError()

    def describe(self):
        raise NotImplementedError()


class OrFilterGroup(EventFilterBaseGroup):
    """Only one child filter has to match"""

    def trigger(self, event: Any) -> bool:
        return any(f.trigger(event) for f in self.filters)

    def describe(self) -> str:
        objs = [f.describe() for f in self.filters]
        return f'({" or ".join(objs)})'


class AndFilterGroup(EventFilterBaseGroup):
    """All child filters have to match"""

    def trigger(self, event: Any) -> bool:
        return all(f.trigger(event) for f in self.filters)

    def describe(self) -> str:
        objs = [f.describe() for f in self.filters]
        return f'({" and ".join(objs)})'
