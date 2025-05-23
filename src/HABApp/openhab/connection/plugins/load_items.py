from __future__ import annotations

import logging
from asyncio import sleep
from typing import TYPE_CHECKING

from immutables import Map

import HABApp.openhab.events
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.openhab.connection.connection import OpenhabConnection, OpenhabContext
from HABApp.openhab.connection.handler import map_null_str
from HABApp.openhab.connection.handler.func_async import async_get_all_items_state, async_get_items, async_get_things
from HABApp.openhab.definitions.websockets.item_value_types import QuantityTypeModel
from HABApp.openhab.item_to_reg import (
    add_thing_to_registry,
    add_to_registry,
    fresh_item_sync,
    get_thing_status_from_resp,
    remove_from_registry,
    remove_thing_from_registry,
)


if TYPE_CHECKING:
    from HABApp.core.lib import InstantView
    from HABApp.openhab.definitions.rest import ThingResp


log = logging.getLogger('HABApp.openhab.items')
Items = uses_item_registry()


class LoadOpenhabItemsPlugin(BaseConnectionPlugin[OpenhabConnection]):

    async def on_connected(self, context: OpenhabContext) -> None:
        # The context will be created fresh for each connect
        if not context.created_items and not context.created_things:
            await self.load_items(context)
            await self.load_things(context)

        # We create the same plugin twice because it uses the same logic to load the objects,
        # One plugin instance will create the objects the other one will sync the state.
        # That's why this is in the else branch
        else:
            # Sleep so we make sure that the openhab event handler is running
            await sleep(0.1)

            # First two delays are 0: First sync and the completion check after the first sync
            delays = (0, 0, *(2 ** i for i in range(6)))

            if context.created_items:
                for d in delays:
                    await sleep(d)
                    if not await self.sync_items(context):
                        break
                else:
                    log.warning('Item state sync failed!')

            if context.created_things:
                for d in delays:
                    await sleep(d)
                    if not await self.sync_things(context):
                        break
                else:
                    log.warning('Thing sync failed!')

    async def load_items(self, context: OpenhabContext) -> None:
        from HABApp.openhab.map_items import map_item
        OpenhabItem = HABApp.openhab.items.OpenhabItem

        log.debug('Requesting items')
        items = await async_get_items()
        items_len = len(items)
        log.debug(f'Got response with {items_len} items')

        fresh_item_sync()

        # add all items
        for item in items:
            new_item = map_item(
                item.name, item.type, map_null_str(item.state), item.label,
                frozenset(item.tags), frozenset(item.groups), item.metadata
            )

            # error
            if new_item is None:
                continue
            add_to_registry(new_item, set_value=True)

        # remove items which are no longer available
        ist = set(Items.get_item_names())
        soll = {item.name for item in items}
        for k in ist - soll:
            if isinstance(Items.get_item(k), OpenhabItem):
                remove_from_registry(k)

        log.info(f'Updated {items_len:d} Items')

        created_items: dict[str, tuple[OpenhabItem, InstantView]] = {
            i.name: (i, i.last_update) for i in Items.get_items() if isinstance(i, OpenhabItem)
        }
        context.created_items.update(created_items)

    async def sync_items(self, context: OpenhabContext):
        log.debug('Starting item state sync')
        created_items = context.created_items

        items = await async_get_all_items_state()

        synced = 0
        for item in items:
            # if the item is still None it was not initialized during the start of the item event listener
            if (new_state := map_null_str(item.state)) is None:
                continue

            existing_item, existing_item_update = created_items[item.name]

            # UoM item handling
            if item.type.startswith('Number:'):
                new_value = QuantityTypeModel.get_value_from_state(new_state)
            else:
                new_value = existing_item._state_from_oh_str(new_state)

            if existing_item.value != new_value and existing_item.last_update == existing_item_update:
                existing_item.value = new_value
                log.debug(f'Re-synced value of {item.name:s}')
                synced += 1

        log.debug('Item state sync complete')
        return synced

    async def load_things(self, context: OpenhabContext) -> None:
        Thing = HABApp.openhab.items.Thing

        # try to update things, too
        log.debug('Requesting things')

        things = await async_get_things()
        thing_count = len(things)
        log.debug(f'Got response with {thing_count:d} things')

        created_things = {}
        for thing in things:
            t = add_thing_to_registry(thing)
            created_things[t.name] = (t, t.last_update)

        context.created_things.update(created_things)

        # remove things which were deleted
        ist = set(Items.get_item_names())
        soll = {thing.uid for thing in things}
        for k in ist - soll:
            if isinstance(Items.get_item(k), Thing):
                remove_thing_from_registry(k)
        log.info(f'Updated {thing_count:d} Things')

    async def sync_things(self, context: OpenhabContext):
        log.debug('Starting Thing sync')
        created_things = context.created_things

        synced = 0

        for thing in await async_get_things():
            existing_thing, existing_datetime = created_things[thing.uid]

            if thing_changed(existing_thing, thing) and existing_thing.last_update != existing_datetime:
                new_status, new_status_detail, new_status_description = get_thing_status_from_resp(thing)

                existing_thing.status = new_status
                existing_thing.status_detail = new_status_detail
                existing_thing.status_description = new_status_description
                existing_thing.label = thing.label
                existing_thing.location = thing.location
                existing_thing.configuration = Map(thing.configuration)
                existing_thing.properties = Map(thing.properties)
                log.debug(f'Re-synced {existing_thing.name:s}')
                synced += 1

        log.debug('Thing sync complete')
        return synced


def thing_changed(old: HABApp.openhab.items.Thing, new: ThingResp) -> bool:
    new_status, new_status_detail, new_status_description = get_thing_status_from_resp(new)

    return old.status != new_status or \
        old.status_detail != new_status_detail or \
        old.status_description != new_status_description or \
        old.label != new.label or \
        old.location != new.location or \
        old.configuration != Map(new.configuration) or \
        old.properties != Map(new.properties)
