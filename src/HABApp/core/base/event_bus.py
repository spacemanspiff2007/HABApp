from typing import Any
from HABApp.core.base import EventBusListenerBase


class EventBusBase:
    def post_event(self, topic: str, event: Any):
        raise NotImplementedError()

    def add_listener(self, listener: EventBusListenerBase):
        raise NotImplementedError()

    def remove_listener(self, listener: EventBusListenerBase):
        raise NotImplementedError()

    def remove_all_listeners(self):
        raise NotImplementedError()
