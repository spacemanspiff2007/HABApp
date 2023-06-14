import logging
from asyncio import sleep
from time import monotonic
from typing import TypeVar, Type, Optional

from HABApp.core.internals import uses_item_registry
from HABApp.core.items import BaseItem
from HABApp.openhab.connection_handler import http_connection
from HABApp.openhab.items import Thing, OpenhabItem
from HABApp.runtime import shutdown

log = logging.getLogger('HABApp.openhab.startup')

item_registry = uses_item_registry()

T = TypeVar('T', bound=BaseItem)


def count_none_items() -> int:
    found = 0
    for item in item_registry.get_items():
        if isinstance(item, OpenhabItem) and item.value is None:
            found += 1
    return found


def find_in_registry(type: Type[T]):
    for item in item_registry.get_items():
        if isinstance(item, type):
            return True
    return False


async def wait_for_obj(obj_class: Type[T], timeout: Optional[float] = None):
    start = monotonic()
    while not find_in_registry(obj_class) and not shutdown.requested:
        if timeout is not None and monotonic() - start >= timeout:
            log.warning(f'Timeout while waiting for {obj_class.__class__.__name__}s')
            return None
        await sleep(1)


async def wait_for_openhab():
    # wait until we find the items from openhab
    await wait_for_obj(OpenhabItem)

    # normally we also have things
    await wait_for_obj(Thing, 10)

    # quick return since everything seems to be already started
    if not http_connection.WAITED_FOR_OPENHAB:
        log.debug('Openhab has already been running -> complete')
        return None

    # if we find None items check if they are still getting initialized (e.g. from persistence)
    if this_count := count_none_items():
        log.debug('Some items are still None - waiting for initialisation')

        last_count = -1
        start = monotonic()

        while not shutdown.requested and last_count != this_count:
            await sleep(1.5)

            # timeout so we start eventually
            if monotonic() - start >= 120:
                log.debug('Timeout while waiting for initialisation')
                break

            last_count = this_count
            this_count = count_none_items()

    log.debug('complete')
