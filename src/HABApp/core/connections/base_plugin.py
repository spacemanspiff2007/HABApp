from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final


if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from HABApp.core.connections.base_connection import BaseConnection
    from HABApp.core.connections.plugin_callback import PluginCallbackHandler
    from HABApp.core.lib.asyncio import AsyncioProvider


class BaseConnectionPlugin[T: BaseConnection]:
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


class BaseConnectionPluginConnectedTask[T: BaseConnection](BaseConnectionPlugin[T]):
    def __init__(self, task_coro: Callable[[], Coroutine[Any, Any, Any]], *,
                 task_name: str, name: str | None = None, asyncio_provider: AsyncioProvider) -> None:
        super().__init__(name)
        self.task: Final = asyncio_provider.create_single_task(task_coro, name=task_name)

    async def on_connected(self) -> None:
        self.task.start()

    async def on_disconnected(self) -> None:
        await self.task.cancel_wait()
