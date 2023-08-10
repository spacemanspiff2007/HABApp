from __future__ import annotations

from dataclasses import dataclass
from inspect import signature, iscoroutinefunction
from typing import Awaitable, Callable, Any, TYPE_CHECKING

from ._definitions import ConnectionStatus, CONNECTION_HANDLER_NAME

if TYPE_CHECKING:
    from .base_connection import BaseConnection
    from .base_plugin import BaseConnectionPlugin


@dataclass
class PluginCallbackHandler:
    plugin: BaseConnectionPlugin
    coro: Callable[[...], Awaitable]
    kwargs: tuple[str, ...]
    priority: int

    async def run(self, connection: BaseConnection, context: Any):
        kwargs = {}
        if self.kwargs:
            if 'connection' in self.kwargs:
                kwargs['connection'] = connection
            if 'context' in self.kwargs:
                kwargs['context'] = context

        return await self.coro(**kwargs)

    @staticmethod
    def _get_coro_kwargs(plugin: BaseConnectionPlugin, coro: Callable[[...], Awaitable]):
        if not iscoroutinefunction(coro):
            raise ValueError(f'Coroutine function expected for {plugin.plugin_name}.{coro.__name__}')

        sig = signature(coro)

        kwargs = []
        for name in sig.parameters:
            if name in ('connection', 'context'):
                kwargs.append(name)
            else:
                raise ValueError(f'Invalid parameter name "{name:s}" for {plugin.plugin_name}.{coro.__name__}')
        return tuple(kwargs)

    @classmethod
    def create(cls, plugin: BaseConnectionPlugin, coro: Callable[[...], Awaitable]):
        return cls(plugin, coro, cls._get_coro_kwargs(plugin, coro), plugin.plugin_priority)

    # sorted uses __lt__
    def __lt__(self, other):
        if not isinstance(other, PluginCallbackHandler):
            return NotImplemented
        return self.priority < other.priority

    def sort_func(self, status: ConnectionStatus) -> tuple[int, int]:
        is_handler = self.plugin.plugin_name == CONNECTION_HANDLER_NAME

        # Handler runs first for every step, except disconnect & offline - there it runs last.
        # That way it's possible to do some cleanup in the plugins when we gracefully disconnect
        if status is ConnectionStatus.DISCONNECTED or status is ConnectionStatus.OFFLINE:
            is_handler = not is_handler

        return int(is_handler), self.priority, int(not self.coro.__name__.startswith('_'))
