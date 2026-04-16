from __future__ import annotations

import logging
from asyncio import sleep
from typing import TYPE_CHECKING, Final

from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.lib import ValueChange
from HABApp.core.lib.timeout import Timeout
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.core.shutdown import ShutdownInfo
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.items import OpenhabItem


if TYPE_CHECKING:
    from HABApp.core.internals import ItemRegistry


log = logging.getLogger('HABApp.openhab.startup')


class WaitForPersistenceRestore(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None, *, item_registry: ItemRegistry) -> None:
        self._item_registry: Final = item_registry
        super().__init__(name)

    def count_none_items(self) -> int:
        found = 0
        for item in self._item_registry.get_items():
            if isinstance(item, OpenhabItem) and item.value is None:
                found += 1
        return found

    async def on_connected(self, context: OpenhabContext) -> None:
        if not context.waited_for_openhab:
            log.debug('Openhab has already been running -> complete')
            return None

        none_items: ValueChange[int] = ValueChange()

        # if we find None items check if they are still getting initialized (e.g. from persistence)
        if none_items.set_value(self.count_none_items()).value:
            log.debug('Some items are still None - waiting for initialisation')

            timeout = Timeout(4 * 60)

            # todo: Implement this properly
            shutdown = await HABAPP_PROVIDER.get(ShutdownInfo)

            while not shutdown.is_requested() and none_items.changed:
                await sleep(3)

                # timeout so we start eventually
                if timeout.is_expired():
                    log.debug('Timeout while waiting for initialisation')
                    break

                none_items.set_value(self.count_none_items())

        log.debug('complete')
        return None
