from __future__ import annotations

from typing import Final, TYPE_CHECKING, Generic, TypeVar, Callable, Awaitable, Any

from ..const.topics import TOPIC_CONNECTIONS
from ..internals import uses_post_event
from ..lib import SingleTask
from ..events.habapp_events import HABAppConnectionStateEvent

if TYPE_CHECKING:
    from .plugin_callback import PluginCallbackHandler
    from .base_connection import BaseConnection


T = TypeVar('T', bound='BaseConnection')


class BaseConnectionPlugin(Generic[T]):
    def __init__(self, name: str, priority: int = 0):
        super().__init__()
        self.plugin_connection: T = None
        self.plugin_name: Final = name
        self.plugin_priority: int = priority
        self.plugin_callbacks: dict[str, PluginCallbackHandler] = {}


post_event = uses_post_event()


class ConnectionEventMixin:
    def __init__(self):
        self.__last_report = None

    def __post_event(self, connection: BaseConnection):
        if (status := connection.status.status.value) != self.__last_report:
            self.__last_report = status
            post_event(TOPIC_CONNECTIONS, HABAppConnectionStateEvent(connection.name, status))

    async def _on_online__event(self, connection: 'BaseConnection'):
        self.__post_event(connection)

    async def _on_disconnected__event(self, connection: 'BaseConnection'):
        self.__post_event(connection)


class BaseConnectionPluginConnectedTask(BaseConnectionPlugin[T]):
    def __init__(self, name: str, priority: int, task_coro: Callable[[], Awaitable[Any]], task_name: str):
        super().__init__(name, priority)
        self.task: Final = SingleTask(task_coro, name=task_name)

    async def _on_connected__task(self):
        self.task.start()

    async def _on_disconnected__task(self):
        await self.task.cancel_wait()
