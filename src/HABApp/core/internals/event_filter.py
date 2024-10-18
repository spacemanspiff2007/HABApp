from typing import Any


class EventFilterBase:
    def trigger(self, event: Any) -> bool:
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f'<{self.describe()} at 0x{id(self):X}>'
