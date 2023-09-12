from __future__ import annotations

import logging
from asyncio import sleep
from time import monotonic

from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.items import OpenhabItem
from HABApp.runtime import shutdown

log = logging.getLogger('HABApp.openhab.startup')

item_registry = uses_item_registry()


def count_none_items() -> int:
    found = 0
    for item in item_registry.get_items():
        if isinstance(item, OpenhabItem) and item.value is None:
            found += 1
    return found


class WaitForPersistenceRestore(BaseConnectionPlugin[OpenhabConnection]):

    async def on_connected(self, context: OpenhabContext):
        if context.waited_for_openhab:
            log.debug('Openhab has already been running -> complete')
            return None

        # if we find None items check if they are still getting initialized (e.g. from persistence)
        if this_count := count_none_items():
            log.debug('Some items are still None - waiting for initialisation')

            last_count = -1
            start = monotonic()

            while not shutdown.requested and last_count != this_count:
                await sleep(2)

                # timeout so we start eventually
                if monotonic() - start >= 180:
                    log.debug('Timeout while waiting for initialisation')
                    break

                last_count = this_count
                this_count = count_none_items()

        log.debug('complete')
