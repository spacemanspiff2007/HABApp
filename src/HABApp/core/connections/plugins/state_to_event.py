from __future__ import annotations

from typing import TYPE_CHECKING, Final

from HABApp.core.connections import BaseConnection, BaseConnectionPlugin
from HABApp.core.const.topics import TOPIC_CONNECTIONS
from HABApp.core.events.habapp_events import HABAppConnectionStateEvent


if TYPE_CHECKING:
    from HABApp.core.internals import EventBus


class ConnectionStateToEventBusPlugin(BaseConnectionPlugin):
    _DEFAULT_PRIORITY = 100_000

    def __init__(self, name: str | None = None, *, event_bus: EventBus) -> None:
        super().__init__(name)
        self.__last_report = None
        self._event_bus: Final = event_bus

    def __post_event(self, connection: BaseConnection) -> None:
        if (status := connection.status.status.value) != self.__last_report:
            self._event_bus.post_event(TOPIC_CONNECTIONS, HABAppConnectionStateEvent(connection.name, status))
            self.__last_report = status

    async def on_online(self, connection: BaseConnection) -> None:
        self.__post_event(connection)

    async def on_disconnected(self, connection: BaseConnection) -> None:
        self.__post_event(connection)
