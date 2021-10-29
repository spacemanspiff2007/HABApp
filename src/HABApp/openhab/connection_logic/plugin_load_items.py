import logging

import HABApp
from HABApp.core import Items
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.map_items import map_item
from ._plugin import OnConnectPlugin
from ..interface_async import async_get_items, async_get_things
from HABApp.openhab.item_to_reg import add_to_registry, fresh_item_sync

log = logging.getLogger('HABApp.openhab.items')


class LoadAllOpenhabItems(OnConnectPlugin):

    @ignore_exception
    async def on_connect_function(self):
        data = await async_get_items(disconnect_on_error=True, all_metadata=True)
        if data is None:
            return None

        fresh_item_sync()

        found_items = len(data)
        for _dict in data:
            item_name = _dict['name']
            new_item = map_item(item_name, _dict['type'], _dict['state'],
                                frozenset(_dict['tags']), frozenset(_dict['groupNames']),
                                _dict.get('metadata', {}))   # type: HABApp.openhab.items.OpenhabItem
            if new_item is None:
                continue
            add_to_registry(new_item, True)

        # remove items which are no longer available
        ist = set(Items.get_all_item_names())
        soll = {k['name'] for k in data}
        for k in ist - soll:
            if isinstance(Items.get_item(k), HABApp.openhab.items.OpenhabItem):
                Items.pop_item(k)

        log.info(f'Updated {found_items:d} Items')

        # try to update things, too
        data = await async_get_things(disconnect_on_error=True)
        if data is None:
            return None

        Thing = HABApp.openhab.items.Thing
        for t_dict in data:
            name = t_dict['UID']
            try:
                thing = Items.get_item(name)
                if not isinstance(thing, Thing):
                    log.warning(f'Item {name} has the wrong type ({type(thing)}), expected Thing')
                    thing = Thing(name)
            except Items.ItemNotFoundException:
                thing = Thing(name)

            thing.status = t_dict['statusInfo']['status']
            Items.add_item(thing)

        # remove things which were deleted
        ist = set(Items.get_all_item_names())
        soll = {k['UID'] for k in data}
        for k in ist - soll:
            if isinstance(Items.get_item(k), Thing):
                Items.pop_item(k)

        log.info(f'Updated {len(data):d} Things')
        return None


PLUGIN_LOAD_ITEMS = LoadAllOpenhabItems.create_plugin()
