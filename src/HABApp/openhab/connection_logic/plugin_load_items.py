import logging

import HABApp
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.item_to_reg import add_to_registry, fresh_item_sync, remove_from_registry, \
    remove_thing_from_registry, add_thing_to_registry
from HABApp.openhab.map_items import map_item
from ._plugin import OnConnectPlugin
from ..interface_async import async_get_items, async_get_things
from ...core.internals import uses_item_registry

log = logging.getLogger('HABApp.openhab.items')

Items = uses_item_registry()


class LoadAllOpenhabItems(OnConnectPlugin):

    @ignore_exception
    async def on_connect_function(self):
        data = await async_get_items(all_metadata=True)
        if data is None:
            return None

        fresh_item_sync()

        found_items = len(data)
        for _dict in data:
            item_name = _dict['name']
            new_item = map_item(item_name, _dict['type'], _dict['state'], _dict.get('label'),
                                frozenset(_dict['tags']), frozenset(_dict['groupNames']),
                                _dict.get('metadata', {}))   # type: HABApp.openhab.items.OpenhabItem
            if new_item is None:
                continue
            add_to_registry(new_item, True)

        # remove items which are no longer available
        ist = set(Items.get_item_names())
        soll = {k['name'] for k in data}
        for k in ist - soll:
            if isinstance(Items.get_item(k), HABApp.openhab.items.OpenhabItem):
                remove_from_registry(k)

        log.info(f'Updated {found_items:d} Items')

        # try to update things, too
        data = await async_get_things()

        Thing = HABApp.openhab.items.Thing
        for thing_cfg in data:
            add_thing_to_registry(thing_cfg)

        # remove things which were deleted
        ist = set(Items.get_item_names())
        soll = {k.uid for k in data}
        for k in ist - soll:
            if isinstance(Items.get_item(k), Thing):
                remove_thing_from_registry(k)

        log.info(f'Updated {len(data):d} Things')
        return None


PLUGIN_LOAD_ITEMS = LoadAllOpenhabItems.create_plugin()
