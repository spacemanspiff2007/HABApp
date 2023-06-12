import logging
from datetime import datetime
from typing import Dict, Tuple, Optional

import HABApp
from HABApp.core.wrapper import ignore_exception
from HABApp.openhab.item_to_reg import add_to_registry, fresh_item_sync, remove_from_registry, \
    remove_thing_from_registry, add_thing_to_registry
from HABApp.openhab.map_items import map_item
from ._plugin import OnConnectPlugin
from ..definitions import QuantityValue
from ..interface_async import async_get_items, async_get_things
from ..items import OpenhabItem
from ...core.internals import uses_item_registry

log = logging.getLogger('HABApp.openhab.items')

Items = uses_item_registry()


def map_null(value: str) -> Optional[str]:
    if value == 'NULL' or value == 'UNDEF':
        return None
    return value


class LoadAllOpenhabItems(OnConnectPlugin):

    @ignore_exception
    async def on_connect_function(self):
        log.debug('Requesting items')
        data = await async_get_items(all_metadata=True)
        if data is None:
            return None

        found_items = len(data)
        log.debug(f'Got response with {found_items} items')

        fresh_item_sync()

        for _dict in data:
            item_name = _dict['name']
            new_item = map_item(item_name, _dict['type'], map_null(_dict['state']), _dict.get('label'),
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

        # Sync missed updates (e.g. where we got a value updated/changed event during the item request)
        # Some bindings poll the item states directly after persistence and we might miss those during startup
        log.debug('Starting item state sync')
        created_items: Dict[str, Tuple[OpenhabItem, datetime]] = {
            i.name: (i, i.last_update) for i in Items.get_items() if isinstance(i, OpenhabItem)
        }
        if (data := await async_get_items(only_item_state=True)) is None:
            return None

        for _dict in data:
            item_name = _dict['name']

            # if the item is still None it was not initialized during the item request
            if (_new_value := map_null(_dict['state'])) is None:
                continue

            # UoM item handling
            if ':' in _dict['type']:
                _new_value, _ = QuantityValue.split_unit(_new_value)

            existing_item, existing_item_update = created_items[item_name]
            # noinspection PyProtectedMember
            _new_value = existing_item._state_from_oh_str(_new_value)

            if existing_item.value != _new_value and existing_item.last_update == existing_item_update:
                existing_item.value = _new_value
                log.debug(f'Re-synced value of {item_name:s}')
        log.debug('Item state sync complete')

        # try to update things, too
        log.debug('Requesting things')

        data = await async_get_things()

        found_things = len(data)
        log.debug(f'Got response with {found_things} things')

        Thing = HABApp.openhab.items.Thing
        for thing_cfg in data:
            add_thing_to_registry(thing_cfg)

        # remove things which were deleted
        ist = set(Items.get_item_names())
        soll = {k.uid for k in data}
        for k in ist - soll:
            if isinstance(Items.get_item(k), Thing):
                remove_thing_from_registry(k)

        log.info(f'Updated {found_things:d} Things')
        return None


PLUGIN_LOAD_ITEMS = LoadAllOpenhabItems.create_plugin()
