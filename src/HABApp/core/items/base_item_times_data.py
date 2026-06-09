from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final, override

from whenever import Instant, TimeDelta

from HABApp.core.asyncio import run_func_from_async
from HABApp.core.lib import DebouncedCallBase, DebouncedCallRegistry
from HABApp.core.logger import HABAppWarning
from HABApp.core.provider import HABAPP_PROVIDER


if TYPE_CHECKING:
    from HABApp.core.items import BaseItem
    from HABApp.core.items.base_item_watch import DebouncedEventBase


@HABAPP_PROVIDER.register
class ItemTimesBackup(DebouncedCallBase):
    __slots__ = ('_data', )

    def __init__(self, registry: DebouncedCallRegistry) -> None:
        super().__init__(TimeDelta(hours=48), registry)

        self._data: Final[
            dict[str, tuple[Instant, tuple[DebouncedEventBase, ...], tuple[DebouncedEventBase, ...]]]
        ] = {}

    # noinspection PyProtectedMember
    def _backup(self, item: BaseItem) -> None:
        f_update = item._last_update._factories
        f_change = item._last_change._factories

        self._data[item.name] = (Instant.now(), f_update, f_change)

        for f in f_update + f_change:
            f.cancel()
        self.reset()

    # noinspection PyProtectedMember
    def _restore(self, item: BaseItem) -> None:
        if (objs := self._data.get(item.name)) is None:
            return None

        _, f_update, f_change = objs

        item._last_update._factories = f_update
        item._last_change._factories = f_change

    def add_to_registry(self, item: BaseItem) -> None:
        run_func_from_async(self._restore, item)

    def remove_from_registry(self, item: BaseItem) -> None:
        run_func_from_async(self._backup, item)

    @override
    async def _run(self) -> None:
        to_del: Final[list[str]] = []
        now: Final = Instant.now()
        timeout: Final = self._timeout

        for name, (time, _, _) in self._data.items():
            if (diff := now - time) < timeout:
                continue

            to_del.append(name)
            # show a warning because otherwise it's not clear what is happening
            w = HABAppWarning(logging.getLogger('HABApp.Item'))
            hrs = diff.in_hours()
            w.add(
                f'Item {name} has been deleted {hrs:.0f}h ago even though it has item watchers. '
                f'If it will be added again the watchers have to be created again, too!'
            )
            w.dump()

        for name in to_del:
            self._data.pop(name)
