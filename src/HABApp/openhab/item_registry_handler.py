from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from immutables import Map

import HABApp
from HABApp.core.logger import log_warning
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.openhab.definitions.things import (
    THING_STATUS_DEFAULT,
    THING_STATUS_DETAIL_DEFAULT,
    ThingStatusDetailEnum,
    ThingStatusEnum,
)


if TYPE_CHECKING:
    from HABApp.core.internals import ItemRegistry
    from HABApp.openhab.definitions.rest import ThingResp
    from HABApp.openhab.events import ThingAddedEvent
    from HABApp.openhab.item_factory import OhItemFactory
    from HABApp.openhab.items import OpenhabItem, Thing

log = logging.getLogger('HABApp.openhab.items')


@HABAPP_PROVIDER.register
class OhItemRegistryHandler:
    __slots__ = ('_group_members', '_ir')

    def __init__(self, ir: ItemRegistry) -> None:
        self._ir: Final = ir
        self._group_members: Final[dict[str, tuple[str, ...]]] = {}

    def add_to_registry(self, item: OpenhabItem, *, set_value: bool = False) -> None:
        ir: Final = self._ir
        name: Final = item.name

        for grp in item.groups:
            self._group_members[grp] = tuple(sorted(set(self._group_members.get(grp, ())) | {name}))

        if not ir.item_exists(name):
            ir.add_item(item)
            return None

        existing = ir.get_item(name)
        if isinstance(existing, item.__class__):
            # If we load directly through the API and not through an event we have to set the value
            if set_value:
                existing.set_value(item.value)

            # remove old groups
            if to_remove := frozenset(existing.groups) - frozenset(item.groups):
                self._remove_name_from_groups(name, to_remove)

            # same type - it was only an item update (e.g. label)!
            # noinspection PyProtectedMember
            existing._update_item_definition(item)
            return None

        log_warning(log, f'Item type changed from {existing.__class__} to {item.__class__}')

        # Replace existing item with the updated definition
        ir.pop_item(name)
        ir.add_item(item)
        return None

    def _remove_name_from_groups(self, name: str, groups: frozenset[str]) -> None:
        for group in groups:
            new_members = set(self._group_members.get(group, ())) - {name}
            if new_members:
                self._group_members[group] = tuple(sorted(new_members))
            else:
                self._group_members.pop(group, None)

    def remove_from_registry(self, name: str) -> None:
        ir: Final = self._ir

        if not ir.item_exists(name):
            return None

        item = ir.get_item(name)  # type: HABApp.openhab.items.OpenhabItem
        self._remove_name_from_groups(name, item.groups)
        ir.pop_item(name)
        return None

    def get_group_members(self, group_name: str) -> tuple[OpenhabItem, ...]:
        return tuple(self._ir.get_item(name) for name in self._group_members.get(group_name, ()))

    def fresh_item_sync(self) -> None:
        self._group_members.clear()

# ----------------------------------------------------------------------------------------------------------------------
# Thing handling
# ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_thing_status_from_resp(
            obj: ThingResp | None) -> tuple[ThingStatusEnum, ThingStatusDetailEnum, str]:
        if obj is None:
            return THING_STATUS_DEFAULT, THING_STATUS_DETAIL_DEFAULT, ''
        return (
            obj.status.status,
            obj.status.detail,
            obj.status.description if obj.status.description is not None else ''
        )

    def add_thing_to_registry(self, data: ThingResp | ThingAddedEvent, item_factory: OhItemFactory) -> Thing:
        ir: Final = self._ir

        if isinstance(data, HABApp.openhab.events.thing_events.ThingAddedEvent):
            name = data.name
            status, status_detail, status_description = self.get_thing_status_from_resp(None)
        elif isinstance(data, HABApp.openhab.definitions.rest.ThingResp):
            name = data.uid
            status, status_detail, status_description = self.get_thing_status_from_resp(data)
        else:
            raise TypeError()

        if ir.item_exists(name):
            existing = ir.get_item(name)
            if isinstance(existing, HABApp.openhab.items.Thing):
                new_thing = existing
            else:
                # Replace existing item with the correct type
                new_thing = item_factory.create_thing(name=name)
                log_warning(log, f'Item type changed from {existing.__class__} to {new_thing.__class__}')
                ir.pop_item(name)
        else:
            new_thing = item_factory.create_thing(name=name)

        new_thing.status = status
        new_thing.status_detail = status_detail
        new_thing.status_description = status_description
        new_thing.label = data.label
        new_thing.location = data.location
        new_thing.configuration = Map(data.configuration)
        new_thing.properties = Map(data.properties)
        return ir.add_item(new_thing)

    def remove_thing_from_registry(self, name: str) -> None:
        ir: Final = self._ir

        if not ir.item_exists(name):
            return None
        ir.pop_item(name)
        return None
