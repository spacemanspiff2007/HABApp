from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Final

import HABApp
from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.definitions.helpers.log_table import Table


if TYPE_CHECKING:
    from HABApp.openhab.definitions.rest import ThingResp


PING_CONFIG: Final = CONFIG.openhab.ping

Items = uses_item_registry()


class ThingOverviewPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.do_run = True

    async def on_online(self) -> None:
        if not self.do_run:
            return None

        # don't run this after the connect, let the rules load etc.
        await asyncio.sleep(90)
        self.do_run = False

        self.draw_table(await HABApp.openhab.interface_async.async_get_things())

    @HABApp.core.wrapper.ignore_exception
    def draw_table(self, thing_data: tuple[ThingResp, ...]) -> None:

        thing_table = Table('Things')
        thing_stat = thing_table.add_column('Status', align='^')
        thing_label = thing_table.add_column('Label')
        thing_location = thing_table.add_column('Location')
        thing_type = thing_table.add_column('Thing type')
        thing_uid = thing_table.add_column('Thing UID')

        for node in thing_data:
            uid = node.uid
            type_uid = node.thing_type

            thing_uid.add(uid)
            thing_type.add(type_uid)
            thing_label.add(node.label)
            thing_stat.add(node.status.status)
            thing_location.add(node.location if node.location is not None else '')

        log = logging.getLogger('HABApp.openhab.things')
        for line in thing_table.get_lines(sort_columns=[thing_uid]):
            log.info(line)
