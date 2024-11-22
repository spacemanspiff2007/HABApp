from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from immutables import Map

import HABApp
from HABApp.core.internals import uses_item_registry
from HABApp.core.logger import log_warning
from HABApp.openhab.definitions.things import (
    THING_STATUS_DEFAULT,
    THING_STATUS_DETAIL_DEFAULT,
    ThingStatusDetailEnum,
    ThingStatusEnum,
)


if TYPE_CHECKING:
    from HABApp.openhab.definitions.rest import ThingResp
    from HABApp.openhab.events import ThingAddedEvent
    from HABApp.openhab.items import OpenhabItem

log = logging.getLogger('HABApp.openhab.items')

Items = uses_item_registry()


def add_to_registry(item: OpenhabItem, set_value=False):
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
        existing.label    = item.label
        existing.tags     = item.tags
        existing.groups   = item.groups
        existing.metadata = item.metadata
        return None

    log_warning(log, f'Item type changed from {existing.__class__} to {item.__class__}')

    # Replace existing item with the updated definition
    Items.pop_item(name)
    Items.add_item(item)
    return None


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


MEMBERS: dict[str, set[str]] = {}


def fresh_item_sync() -> None:
    MEMBERS.clear()


def get_members(group_name: str) -> tuple[OpenhabItem, ...]:
    ret = []
    for name in MEMBERS.get(group_name, []):
        item = Items.get_item(name)  # type: OpenhabItem
        ret.append(item)
    return tuple(sorted(ret, key=lambda x: x.name))


# ----------------------------------------------------------------------------------------------------------------------
# Thing handling
# ----------------------------------------------------------------------------------------------------------------------

def get_thing_status_from_resp(
        obj: ThingResp | None) -> tuple[ThingStatusEnum, ThingStatusDetailEnum, str]:
    if obj is None:
        return THING_STATUS_DEFAULT, THING_STATUS_DETAIL_DEFAULT, ''
    return (
        obj.status.status,
        obj.status.detail,
        obj.status.description if obj.status.description is not None else ''
    )


def add_thing_to_registry(data: ThingResp | ThingAddedEvent):

    if isinstance(data, HABApp.openhab.events.thing_events.ThingAddedEvent):
        name = data.name
        status, status_detail, status_description = get_thing_status_from_resp(None)
    elif isinstance(data, HABApp.openhab.definitions.rest.ThingResp):
        name = data.uid
        status, status_detail, status_description = get_thing_status_from_resp(data)
    else:
        raise TypeError()

    if Items.item_exists(name):
        existing = Items.get_item(name)
        if isinstance(existing, HABApp.openhab.items.Thing):
            new_thing = existing
        else:
            # Replace existing item with the correct type
            new_thing = HABApp.openhab.items.Thing(name=name)
            log_warning(log, f'Item type changed from {existing.__class__} to {new_thing.__class__}')
            Items.pop_item(name)
    else:
        new_thing = HABApp.openhab.items.Thing(name=name)

    new_thing.status = status
    new_thing.status_detail = status_detail
    new_thing.status_description = status_description
    new_thing.label = data.label
    new_thing.location = data.location
    new_thing.configuration = Map(data.configuration)
    new_thing.properties = Map(data.properties)
    return Items.add_item(new_thing)


def remove_thing_from_registry(name: str):
    if not Items.item_exists(name):
        return None
    return Items.pop_item(name)
