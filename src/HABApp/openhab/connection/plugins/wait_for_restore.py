from __future__ import annotations

import logging
from asyncio import sleep

from HABApp.core import shutdown
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.core.lib import ValueChange
from HABApp.core.lib.timeout import Timeout
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.items import OpenhabItem


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
        if not context.waited_for_openhab:
            log.debug('Openhab has already been running -> complete')
            return None

        none_items: ValueChange[int] = ValueChange()

        # if we find None items check if they are still getting initialized (e.g. from persistence)
        if none_items.set_value(count_none_items()).value:
            log.debug('Some items are still None - waiting for initialisation')

            timeout = Timeout(4 * 60)
            while not shutdown.is_requested() and none_items.changed:
                await sleep(3)

                # timeout so we start eventually
                if timeout.is_expired():
                    log.debug('Timeout while waiting for initialisation')
                    break

                none_items.set_value(count_none_items())

        log.debug('complete')
