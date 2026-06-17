from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.logger import log_warning
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.connection.handler import OpenHabAsyncInterface


if TYPE_CHECKING:
    from HABApp.core.internals import ItemRegistry


PING_CONFIG: Final = CONFIG.openhab.ping


class BrokenLinksPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None, *,
                 item_registry: ItemRegistry, interface: OpenHabAsyncInterface) -> None:

        super().__init__(name)

        self._item_registry: Final = item_registry
        self._interface: Final = interface

        self.do_run: bool = True

    async def on_online(self) -> None:
        if not self.do_run:
            return None
        self.do_run = False

        log: Final = logging.getLogger('HABApp.openhab.links')

        things: Final = await self._interface.get_things()
        links: Final = await self._interface.get_links()

        available_things: Final = {t.uid for t in things}
        available_channels: Final = {c.uid for t in things for c in t.channels}

        for link in sorted(links, key=lambda x: x.channel):
            if not self._item_registry.item_exists(link.item):
                log_warning(log, f'Item "{link.item}" does not exist! '
                                 f'(link between item "{link.item:s}" and channel "{link.channel:s}")')
                continue

            if link.channel not in available_channels:
                # check if the thing exists
                thing_uid, channel_id = link.channel.rsplit(':', maxsplit=1)
                if thing_uid in available_things:
                    log_warning(log, f'Channel "{channel_id}" on thing "{thing_uid:s}" does not exist! '
                                     f'(link between item "{link.item:s}" and channel "{link.channel:s}")')
                else:
                    log_warning(log, f'Thing "{thing_uid:s}" does not exist! '
                                     f'(link between item "{link.item:s}" and channel "{link.channel:s}")')

        return None
