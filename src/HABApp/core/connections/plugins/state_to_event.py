from __future__ import annotations

from HABApp.core.connections import BaseConnection, BaseConnectionPlugin
from HABApp.core.const.topics import TOPIC_CONNECTIONS
from HABApp.core.events.habapp_events import HABAppConnectionStateEvent
from HABApp.core.internals import uses_post_event


post_event = uses_post_event()


class ConnectionStateToEventBusPlugin(BaseConnectionPlugin):
    def __init__(self):
        super().__init__(priority=-100_000)
        self.__last_report = None

    def __post_event(self, connection: BaseConnection):
        if (status := connection.status.status.value) != self.__last_report:
            post_event(TOPIC_CONNECTIONS, HABAppConnectionStateEvent(connection.name, status))
            self.__last_report = status

    async def on_online(self, connection: BaseConnection):
        self.__post_event(connection)

    async def on_disconnected(self, connection: BaseConnection):
        self.__post_event(connection)
