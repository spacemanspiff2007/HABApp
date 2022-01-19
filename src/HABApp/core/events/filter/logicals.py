from typing import Any

from HABApp.core.events.filter.base import EventFilterBaseGroup


class OrFilterGroup(EventFilterBaseGroup):
    """Only one child filter has to match"""

    def trigger(self, event: Any) -> bool:
        for f in self.filters:
            if f.trigger(event):
                return True
        return False

    def describe(self) -> str:
        or_objs = [str(f) for f in self.filters]
        return f'<{self.__class__.__name__} {" or ".join(or_objs)}>'


class AndFilterGroup(EventFilterBaseGroup):
    """All child filters have to match"""

    def trigger(self, event: Any) -> bool:
        for f in self.filters:
            if not f.trigger(event):
                return False
        return True

    def describe(self) -> str:
        or_objs = [str(f) for f in self.filters]
        return f'<{self.__class__.__name__} {" and ".join(or_objs)}>'
