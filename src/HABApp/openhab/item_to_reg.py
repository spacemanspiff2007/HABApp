import logging

import HABApp
from HABApp.core import Items
from HABApp.core.logger import log_warning

log = logging.getLogger('HABApp.openhab.items')


def add_item_to_registry(item: 'HABApp.openhab.items.OpenhabItem', set_value=False):
    if not Items.item_exists(item.name):
        return Items.add_item(item)

    existing = Items.get_item(item.name)
    if isinstance(existing, item.__class__):
        # If we load directly through the API and not through an event we have to set the value
        if set_value:
            existing.set_value(item.value)

        # same type - it was only an item update (e.g. label)!
        existing.tags = item.tags
        existing.groups = item.groups
        return None

    log_warning(log, f'Item type changed from {existing.__class__} to {item.__class__}')

    # Replace existing item with the updated definition
    Items.pop_item(item.name)
    Items.add_item(item)
