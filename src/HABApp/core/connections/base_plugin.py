from __future__ import annotations

from typing import Final, TYPE_CHECKING, Generic, TypeVar, Callable, Awaitable, Any

from ..lib import SingleTask

if TYPE_CHECKING:
    from .plugin_callback import PluginCallbackHandler
    from .base_connection import BaseConnection


T = TypeVar('T', bound='BaseConnection')


class BaseConnectionPlugin(Generic[T]):
    def __init__(self, name: str, priority: int = 0):
        self.plugin_connection: T = None
        self.plugin_name: Final = name
        self.plugin_priority: int = priority
        self.plugin_callbacks: dict[str, PluginCallbackHandler] = {}


class BaseConnectionPluginConnectedTask(BaseConnectionPlugin[T]):
    def __init__(self, name: str, priority: int, task_coro: Callable[[], Awaitable[Any]], task_name: str):
        super().__init__(name, priority)
        self.task: Final = SingleTask(task_coro, name=task_name)

    async def _on_connected__task(self):
        self.task.start()

    async def _on_disconnected__task(self):
        await self.task.cancel_wait()
