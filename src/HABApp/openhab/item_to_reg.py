import logging
from typing import Dict, Set, Tuple

import HABApp
from HABApp.core.internals import uses_item_registry
from HABApp.core.logger import log_warning

log = logging.getLogger('HABApp.openhab.items')

Items = uses_item_registry()


def add_to_registry(item: 'HABApp.openhab.items.OpenhabItem', set_value=False):
    name = item.name
    for grp in item.groups:
        MEMBERS.setdefault(grp, set()).add(name)

    if not Items.item_exists(name):
        return Items.add_item(item)

    existing = Items.get_item(name)
    if isinstance(existing, item.__class__):
        # If we load directly through the API and not through an event we have to set the value
        if set_value:
            existing.set_value(item.value)

        # remove old groups
        for grp in set(existing.groups) - set(item.groups):
            MEMBERS.get(grp, set()).discard(name)

        # same type - it was only an item update (e.g. label)!
        existing.tags = item.tags
        existing.groups = item.groups
        return None

    log_warning(log, f'Item type changed from {existing.__class__} to {item.__class__}')

    # Replace existing item with the updated definition
    Items.pop_item(name)
    Items.add_item(item)


def remove_from_registry(name: str):
    if not Items.item_exists(name):
        return None

    item = Items.get_item(name)  # type: HABApp.openhab.items.OpenhabItem
    for grp in item.groups:
        MEMBERS.get(grp, set()).discard(name)

    if isinstance(item, HABApp.openhab.items.GroupItem):
        MEMBERS.pop(name, None)

    Items.pop_item(name)
    return None


MEMBERS: Dict[str, Set[str]] = {}


def fresh_item_sync():
    MEMBERS.clear()


def get_members(group_name: str) -> Tuple['HABApp.openhab.items.OpenhabItem', ...]:
    ret = []
    for name in MEMBERS.get(group_name, []):
        item = Items.get_item(name)  # type: HABApp.openhab.items.OpenhabItem
        ret.append(item)
    return tuple(sorted(ret, key=lambda x: x.name))


# ----------------------------------------------------------------------------------------------------------------------
# Thing handling
# ----------------------------------------------------------------------------------------------------------------------
def add_thing_to_registry(thing: 'HABApp.openhab.items.Thing'):
    name = thing.name
    if not Items.item_exists(name):
        Items.add_item(thing)
        return None

    existing = Items.get_item(name)   # type: HABApp.openhab.items.Thing
    if isinstance(existing, HABApp.openhab.items.Thing):
        existing.status = thing.status
        return None

    # Replace existing item with the updated definition
    log_warning(log, f'Item type changed from {existing.__class__} to {thing.__class__}')
    Items.pop_item(name)
    Items.add_item(thing)


def remove_thing_from_registry(name: str):
    if not Items.item_exists(name):
        return None
    return Items.pop_item(name)
