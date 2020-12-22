import HABApp
from HABApp.core.events import AllEvents
from . import WrappedFunction
from typing import Optional, Any


class EventBusListener:
    def __init__(self, topic, callback, event_type=AllEvents,
                 prop_name1: Optional[str] = None, prop_value1: Optional[Any] = None,
                 prop_name2: Optional[str] = None, prop_value2: Optional[Any] = None,
                 ):
        assert isinstance(topic, str), type(topic)
        assert isinstance(callback, WrappedFunction)
        assert prop_name1 is None or isinstance(prop_name1, str), prop_name1
        assert prop_name2 is None or isinstance(prop_name2, str), prop_name2

        self.topic: str = topic
        self.func: WrappedFunction = callback

        self.event_filter = event_type

        # Property filters
        self.prop_name1 = prop_name1
        self.prop_value1 = prop_value1
        self.prop_name2 = prop_name2
        self.prop_value2 = prop_value2

        self.__is_all: bool = self.event_filter is AllEvents
        self.__is_single: bool = not isinstance(self.event_filter, (list, tuple, set))

    def notify_listeners(self, event):
        # We run always
        if self.__is_all:
            self.func.run(event)
            return None

        # single filter
        if self.__is_single:
            if isinstance(event, self.event_filter):
                # If we have property filters wie only trigger when value is set accordingly
                if self.prop_name1 is not None:
                    if getattr(event, self.prop_name1, None) != self.prop_value1:
                        return None
                if self.prop_name2 is not None:
                    if getattr(event, self.prop_name2, None) != self.prop_value2:
                        return None

                self.func.run(event)
            return None

        # Make it possible to specify multiple classes
        for cls in self.event_filter:
            if isinstance(event, cls):
                # If we have property filters wie only trigger when value is set accordingly
                if self.prop_name1 is not None:
                    if getattr(event, self.prop_name1, None) != self.prop_value1:
                        return None
                if self.prop_name2 is not None:
                    if getattr(event, self.prop_name2, None) != self.prop_value2:
                        return None

                self.func.run(event)
                return None

    def cancel(self):
        """Stop listening on the event bus"""
        HABApp.core.EventBus.remove_listener(self)

    def desc(self):
        # return description
        _type = str(self.event_filter)
        if _type.startswith("<class '"):
            _type = _type[8:-2].split('.')[-1]

        _val = ''
        if self.prop_name1 is not None:
            _val += f', {self.prop_name1}=={self.prop_value1}'
        if self.prop_name2 is not None:
            _val += f', {self.prop_name2}=={self.prop_value2}'

        return f'"{self.topic}" (type {_type}{_val})'
