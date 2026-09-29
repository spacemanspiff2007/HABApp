from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final, override

from HABApp.core.events import ItemNoChangeEvent, ItemNoUpdateEvent
from HABApp.core.lib import DebouncedCallBase, DebouncedCallRegistry


if TYPE_CHECKING:
    from HABApp.core.internals import EventBus


log = logging.getLogger('HABApp')


class DebouncedEventBase(DebouncedCallBase):
    __slots__ = ('_eb', '_item', '_secs', '_watchers')

    def __init__(self, timeout: float, item_name: str, registry: DebouncedCallRegistry, event_bus: EventBus) -> None:
        super().__init__(timeout, registry)
        self._eb: Final[EventBus] = event_bus
        self._secs: Final[float] = timeout
        self._item: Final[str] = item_name

        self._watchers: int = 0

    def log_desc(self) -> str:
        return f'{self.event_cls().__name__}({self._item}, {self._secs}s)'

    def _log_watchers(self) -> None:
        log.debug(f'{self.log_desc():s} has now {self._watchers} watcher{"" if self._watchers == 1 else "s"}')

    def watcher_increase(self) -> int:
        self._watchers += 1
        self._log_watchers()
        return self._watchers

    def watcher_decrease(self) -> int:
        self._watchers -= 1
        self._log_watchers()
        return self._watchers

    @override
    def _repr_parts(self) -> str:
        return f' item={self._item}'

    @property
    def seconds(self) -> float:
        return self._secs

    @property
    def item(self) -> str:
        return self._item

    @staticmethod
    def event_cls() -> type[object]:
        raise NotImplementedError()


class DebouncedNoUpdateEvent(DebouncedEventBase):
    async def _run(self) -> None:
        self._eb.post_event(self._item, ItemNoUpdateEvent(self._item, self._secs))

    @override
    @staticmethod
    def event_cls() -> type[ItemNoUpdateEvent]:
        return ItemNoUpdateEvent


class DebouncedNoChangeEvent(DebouncedEventBase):
    async def _run(self) -> None:
        self._eb.post_event(self._item, ItemNoChangeEvent(self._item, self._secs))

    @override
    @staticmethod
    def event_cls() -> type[ItemNoChangeEvent]:
        return ItemNoChangeEvent
