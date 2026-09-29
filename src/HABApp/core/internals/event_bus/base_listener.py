from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from HABApp.core.errors import EventBusAlreadySetError


if TYPE_CHECKING:
    from HABApp.core.internals import EventBus


class EventBusListenerBase:
    def __init__(self, topic: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if not isinstance(topic, str):
            raise TypeError()
        if not topic:
            raise ValueError()
        self.topic: Final = topic
        self._event_bus: EventBus | None = None

    def _set_event_bus(self, event_bus: EventBus) -> None:
        if self._event_bus is not None:
            msg = 'EventBus already set for this listener!'
            raise EventBusAlreadySetError(msg)
        self._event_bus = event_bus

    def _clear_event_bus(self) -> None:
        self._event_bus = None

    def notify_listeners(self, event: Any) -> None:
        raise NotImplementedError()

    def describe(self) -> str:
        raise NotImplementedError()
