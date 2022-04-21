from HABApp.core.const import MISSING
from HABApp.core.const.hints import HINT_ANY_CLASS
from HABApp.core.internals import EventFilterBase


class EventFilter(EventFilterBase):
    """Triggers on event types and optionally on their values, too"""

    def __init__(self, event_class: HINT_ANY_CLASS, **kwargs):
        assert len(kwargs) < 3, 'EventFilter only allows up to two args that will be used to filter'

        self.event_class = event_class

        # Property filters
        self.attr_name1 = None
        self.attr_value1 = None
        self.attr_name2 = None
        self.attr_value2 = None

        for arg, value in kwargs.items():
            if value is MISSING:
                continue

            if arg not in event_class.__annotations__:
                raise AttributeError(f'Filter attribute "{arg}" does not exist for "{event_class.__name__}"')

            if self.attr_name1 is None:
                self.attr_name1 = arg
                self.attr_value1 = value
            elif self.attr_name2 is None:
                self.attr_name2 = arg
                self.attr_value2 = value
            else:
                raise ValueError('Not implemented for more than 2 values!')

    def trigger(self, event) -> bool:
        if not isinstance(event, self.event_class):
            return False

        # Property filter
        if self.attr_name1 is not None:
            if getattr(event, self.attr_name1, None) != self.attr_value1:
                return False

            if self.attr_name2 is not None:
                if getattr(event, self.attr_name2, None) != self.attr_value2:
                    return False

        return True

    def describe(self) -> str:

        values = ''
        if self.attr_name1 is not None:
            values += f', {self.attr_name1}={self.attr_value1}'
        if self.attr_name2 is not None:
            values += f', {self.attr_name2}={self.attr_value2}'

        return f'{self.__class__.__name__}(type={self.event_class.__name__}{values})'


class TypeBoundEventFilter(EventFilter):
    """Class to inherit from if the filter criteria always is a hardcoded instance check"""

    def describe(self) -> str:

        values = ''
        if self.attr_name1 is not None:
            values += f'{self.attr_name1}={self.attr_value1}'
        if self.attr_name2 is not None:
            values += f'{", " if values else ""}{self.attr_name2}={self.attr_value2}'

        return f'{self.__class__.__name__}({values})'
