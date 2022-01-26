from typing import Any, TypeVar
from HABApp.core.base import EventBusListenerBase
from HABApp.core.errors import ObjHasNotBeenReplacedError


def post_event(topic: str, event: Any):
    raise ObjHasNotBeenReplacedError(post_event)


class EventBusBase:
    def post_event(self, topic: str, event: Any):
        raise NotImplementedError()

    def add_listener(self, listener: EventBusListenerBase):
        raise NotImplementedError()

    def remove_listener(self, listener: EventBusListenerBase):
        raise NotImplementedError()

    def remove_all_listeners(self):
        raise NotImplementedError()


TYPE_EVENT_BUS = TypeVar('TYPE_EVENT_BUS', bound=EventBusBase)
