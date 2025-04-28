from __future__ import annotations

import re
from dataclasses import dataclass
from inspect import getmembers, iscoroutinefunction, signature
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from HABApp.core.lib import get_obj_name

from ._definitions import ConnectionStatus


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

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
            msg = f'Invalid name: {m_name} in {obj.plugin_name}'
            raise ValueError(msg)

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
    def _get_coro_kwargs(plugin: BaseConnectionPlugin, coro: Callable[[...], Awaitable]) -> tuple[str, ...]:
        if not iscoroutinefunction(coro):
            msg = f'Coroutine function expected for {plugin.plugin_name}.{get_obj_name(coro)}'
            raise ValueError(msg)

        sig = signature(coro)

        kwargs = []
        for name in sig.parameters:
            if name in ('connection', 'context'):
                kwargs.append(name)
            else:
                msg = f'Invalid parameter name "{name:s}" for {plugin.plugin_name}.{get_obj_name(coro)}'
                raise ValueError(msg)
        return tuple(kwargs)

    @classmethod
    def create(cls, plugin: BaseConnectionPlugin, coro: Callable[[...], Awaitable]) -> Self:
        return cls(plugin, coro, cls._get_coro_kwargs(plugin, coro))
