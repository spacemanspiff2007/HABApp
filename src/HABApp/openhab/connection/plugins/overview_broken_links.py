from __future__ import annotations

import logging
from typing import Final

from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry
from HABApp.core.logger import log_warning
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.connection.handler.func_async import async_get_links, async_get_things

PING_CONFIG: Final = CONFIG.openhab.ping

Items = uses_item_registry()


class BrokenLinksPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None):
        super().__init__(name)
        self.do_run = True

    async def on_online(self):
        if not self.do_run:
            return None
        self.do_run = False

        log = logging.getLogger('HABApp.openhab.links')

        things = await async_get_things()
        links = await async_get_links()

        available_things = {t.uid for t in things}
        available_channels = {c.uid for t in things for c in t.channels}

        for link in sorted(links, key=lambda x: x.channel):
            if not Items.item_exists(link.item):
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
