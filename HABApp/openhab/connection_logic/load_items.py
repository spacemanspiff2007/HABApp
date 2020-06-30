import asyncio
import logging
from typing import Optional

import HABApp
from HABApp.core import Items
from HABApp.core.wrapper import ignore_exception
from ._plugin import PluginBase
from ..interface_async import async_get_items, async_get_things

log = logging.getLogger('HABApp.openhab.items')


class LoadOpenhabItems(PluginBase):
    def __init__(self):
        self.fut: Optional[asyncio.Future] = None

    def setup(self):
        pass

    def on_connect(self):
        self.fut = asyncio.ensure_future(self.update_all_items(), loop=HABApp.core.const.loop)

    def on_disconnect(self):
        if self.fut is not None:
            self.fut.cancel()
            self.fut = None

    @ignore_exception
    async def update_all_items(self):
        data = await async_get_items()
        if data is None:
            return None

        found_items = len(data)
        for _dict in data:
            item_name = _dict['name']
            new_item = HABApp.openhab.map_items(item_name, _dict['type'], _dict['state'])
            if new_item is None:
                continue

            try:
                # if the item already exists and it has the correct type just update its state
                # Since we load the items before we load the rules this should actually never happen
                existing_item = Items.get_item(item_name)   # type: HABApp.core.items.BaseValueItem
                if isinstance(existing_item, new_item.__class__):
                    existing_item.set_value(new_item.value)  # use the converted state from the new item here
                    new_item = existing_item
            except Items.ItemNotFoundException:
                pass

            # create new item or change item type
            Items.set_item(new_item)

        # remove items which are no longer available
        ist = set(Items.get_all_item_names())
        soll = {k['name'] for k in data}
        for k in ist - soll:
            if isinstance(Items.get_item(k), HABApp.openhab.items.OpenhabItem):
                Items.pop_item(k)

        log.info(f'Updated {found_items:d} Items')


        # try to update things, too
        data = await async_get_things()
        if data is None:
            return None

        Thing = HABApp.openhab.items.Thing
        for t_dict in data:
            name = t_dict['UID']
            try:
                thing = HABApp.core.Items.get_item(name)
                if not isinstance(thing, Thing):
                    log.warning(f'Item {name} has the wrong type ({type(thing)}), expected Thing')
                    thing = Thing(name)
            except HABApp.core.Items.ItemNotFoundException:
                thing = Thing(name)

            thing.status = t_dict['statusInfo']['status']
            HABApp.core.Items.set_item(thing)

        # remove things which were deleted
        ist = set(HABApp.core.Items.get_all_item_names())
        soll = {k['UID'] for k in data}
        for k in ist - soll:
            if isinstance(HABApp.core.Items.get_item(k), Thing):
                HABApp.core.Items.pop_item(k)

        log.info(f'Updated {len(data):d} Things')
        return None


LoadOpenhabItems.create_plugin()
