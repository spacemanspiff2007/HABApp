from __future__ import annotations

import re
from dataclasses import dataclass
from inspect import signature, iscoroutinefunction, getmembers
from typing import Awaitable, Callable, Any, TYPE_CHECKING

from ._definitions import ConnectionStatus

if TYPE_CHECKING:
    from .base_connection import BaseConnection
    from .base_plugin import BaseConnectionPlugin


def get_plugin_callbacks(obj: BaseConnectionPlugin) -> list[tuple[ConnectionStatus, PluginCallbackHandler]]:
    name_to_status = {obj.lower(): obj for obj in ConnectionStatus}
    name_regex = re.compile(f'on_({"|".join(name_to_status)})')

    ret = []
    for m_name, member in getmembers(obj, predicate=lambda x: callable(x)):
        if not m_name.lower().startswith('on_'):
            continue

        if m_name in ('on_application_shutdown', ):
            continue

        if (m := name_regex.fullmatch(m_name)) is None:
            raise ValueError(f'Invalid name: {m_name} in {obj.plugin_name}')

        status = name_to_status[m.group(1)]
        cb = PluginCallbackHandler.create(obj, member)

        ret.append((status, cb))

    return ret


@dataclass
class PluginCallbackHandler:
    plugin: BaseConnectionPlugin
    coro: Callable[[...], Awaitable]
    kwargs: tuple[str, ...]

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
        return cls(plugin, coro, cls._get_coro_kwargs(plugin, coro))
