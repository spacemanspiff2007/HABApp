from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Final, Generic, TypeVar

from HABApp.core.lib import SingleTask


if TYPE_CHECKING:
    from .base_connection import BaseConnection
    from .plugin_callback import PluginCallbackHandler

T = TypeVar('T', bound='BaseConnection')


class BaseConnectionPlugin(Generic[T]):
    def __init__(self, name: str | None = None) -> None:
        super().__init__()

        if name is None:
            name = self.__class__.__name__
            if name[-6:].lower() == 'plugin':
                name = name[:-6]

        self.plugin_connection: T = None
        self.plugin_name: Final = name
        self.plugin_callbacks: dict[str, PluginCallbackHandler] = {}

    def on_application_shutdown(self) -> None:
        pass


class BaseConnectionPluginConnectedTask(BaseConnectionPlugin[T]):
    def __init__(self, task_coro: Callable[[], Awaitable[Any]],
                 task_name: str, name: str | None = None) -> None:
        super().__init__(name)
        self.task: Final = SingleTask(task_coro, name=task_name)

    async def on_connected(self) -> None:
        self.task.start()

    async def on_disconnected(self) -> None:
        await self.task.cancel_wait()
