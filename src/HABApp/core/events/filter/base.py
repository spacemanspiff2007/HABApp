from typing import Tuple, TypeVar, Any


class EventFilterBase:
    def trigger(self, event: Any) -> bool:
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return f'<{self.describe()} at 0x{id(self):X}>'


# Hints for functions that use an item class as an input parameter
TYPE_FILTER_OBJ = TypeVar('TYPE_FILTER_OBJ', bound=EventFilterBase)


class EventFilterBaseGroup(EventFilterBase):
    def __init__(self, *args: TYPE_FILTER_OBJ):
        self.filters: Tuple[TYPE_FILTER_OBJ, ...] = args

    def trigger(self, event) -> bool:
        raise NotImplementedError()

    def describe(self):
        raise NotImplementedError()
