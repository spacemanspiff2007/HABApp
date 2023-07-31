from __future__ import annotations

from dataclasses import dataclass
from inspect import signature, iscoroutinefunction
from typing import Awaitable, Callable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_connection import BaseConnection
    from .base_plugin import BaseConnectionPlugin


@dataclass
class PluginCallbackHandler:
    plugin: BaseConnectionPlugin
    priority: int
    kwargs: tuple[str, ...]
    coro: Callable[[...], Awaitable]

    async def run(self, connection: BaseConnection, context: Any):
        kwargs = {}
        if self.kwargs:
            if 'connection' in self.kwargs:
                kwargs['connection'] = connection
            if 'context' in self.kwargs:
                kwargs['context'] = context

        await self.coro(**kwargs)

    @classmethod
    def create(cls, plugin: BaseConnectionPlugin, coro: Callable[[...], Awaitable]):
        if not iscoroutinefunction(coro):
            raise ValueError(f'Coroutine function expected for {plugin.plugin_name}.{coro.__name__}')

        sig = signature(coro)

        kwargs = []
        for name in sig.parameters:
            if name in ('connection', 'context'):
                kwargs.append(name)
            else:
                raise ValueError(f'Invalid parameter name: {name:s}')

        return cls(plugin, plugin.plugin_priority, tuple(kwargs), coro)

    # sorted uses __lt__
    def __lt__(self, other):
        if not isinstance(other, PluginCallbackHandler):
            return NotImplemented
        return self.priority < other.priority
