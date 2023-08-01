from __future__ import annotations

from dataclasses import dataclass
from inspect import signature, iscoroutinefunction
from typing import Awaitable, Callable, Any, TYPE_CHECKING, Union

from ._definitions import PluginReturn

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

        # Valid return codes are None, PluginReturn or PluginReturn | None
        if sig.return_annotation is not PluginReturn and sig.return_annotation is not sig.empty and \
                sig.return_annotation != Union[PluginReturn, None]:
            raise ValueError(
                f'Coroutine function must return {PluginReturn.__name__} or Optional[{PluginReturn.__name__}]')

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
