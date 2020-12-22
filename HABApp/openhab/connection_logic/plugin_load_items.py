import logging

import HABApp
from HABApp.core import Items
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.map_items import map_item
from ._plugin import OnConnectPlugin
from ..interface_async import async_get_items, async_get_things

log = logging.getLogger('HABApp.openhab.items')


class LoadAllOpenhabItems(OnConnectPlugin):

    @ignore_exception
    async def on_connect_function(self):
        data = await async_get_items()
        if data is None:
            return None

        found_items = len(data)
        for _dict in data:
            item_name = _dict['name']
            new_item = map_item(item_name, _dict['type'], _dict['state'])
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
            Items.add_item(new_item)

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
            HABApp.core.Items.add_item(thing)

        # remove things which were deleted
        ist = set(HABApp.core.Items.get_all_item_names())
        soll = {k['UID'] for k in data}
        for k in ist - soll:
            if isinstance(HABApp.core.Items.get_item(k), Thing):
                HABApp.core.Items.pop_item(k)

        log.info(f'Updated {len(data):d} Things')
        return None


PLUGIN_LOAD_ITEMS = LoadAllOpenhabItems.create_plugin()
