from HABApp.core.internals import EventFilterBase


class NoEventFilter(EventFilterBase):
    """Triggers on all events"""

    def trigger(self, event) -> bool:
        return True

    def describe(self) -> str:
        return f'{self.__class__.__name__}()'
