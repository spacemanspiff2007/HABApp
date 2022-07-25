from typing import TypeVar, Any


class EventFilterBase:
    def trigger(self, event: Any) -> bool:
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return f'<{self.describe()} at 0x{id(self):X}>'


# Hints for functions that use an item class as an input parameter
HINT_EVENT_FILTER_OBJ = TypeVar('HINT_EVENT_FILTER_OBJ', bound=EventFilterBase)
