from __future__ import annotations

from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin_callback import PluginCallbackHandler


class BaseConnectionPlugin:
    def __init__(self, name: str, priority: int = 0):
        self.plugin_name: Final = name
        self.plugin_priority = priority
        self.plugin_callbacks: dict[str, PluginCallbackHandler] = {}
