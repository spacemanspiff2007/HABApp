from typing import Optional

import HABApp
import asyncio
import logging
import time
from HABApp.core.wrapper import log_exception
from ._plugin import PluginBase
from ..definitions.exceptions import OpenhabNotReadyYet, OpenhabDisconnectedError

log = logging.getLogger('HABApp.openhab.ping')


class PingOpenhab(PluginBase):
    def __init__(self):
        self.__ping_sent = 0
        self.__ping_received = 0

        self.listener: Optional[HABApp.core.EventBusListener] = None

        self.fut_ping: Optional[asyncio.Future] = None

    def setup(self):
        HABApp.config.CONFIG.openhab.ping.subscribe_for_changes(self.cfg_changed)
        self.cfg_changed()

    def on_connect(self):
        if not self.IS_CONNECTED:
            return None

        if not HABApp.config.CONFIG.openhab.ping.enabled:
            return None

        self.fut_ping = asyncio.ensure_future(self.async_ping(), loop=HABApp.core.const.loop)

    def on_disconnect(self):
        if self.listener is not None:
            self.listener.cancel()
            self.listener = None

        if self.fut_ping is not None:
            self.fut_ping.cancel()
            self.fut_ping = None

    def cfg_changed(self):
        self.on_disconnect()

        if not HABApp.config.CONFIG.openhab.ping.enabled:
            return None

        self.listener = HABApp.core.EventBusListener(
            HABApp.config.CONFIG.openhab.ping.item,
            HABApp.core.WrappedFunction(self.ping_received),
            HABApp.openhab.events.ItemStateEvent
        )
        HABApp.core.EventBus.add_listener(self.listener)

        self.on_connect()

    async def ping_received(self, event):
        self.__ping_received = time.time()

    @log_exception
    async def async_ping(self):
        await asyncio.sleep(3)

        log.debug('Started ping')
        try:
            while True:
                await HABApp.openhab.interface_async.async_post_update(
                    HABApp.config.CONFIG.openhab.ping.item,
                    f'{(self.__ping_received - self.__ping_sent) * 1000:.1f}' if self.__ping_received else '0'
                )
                self.__ping_sent = time.time()
                await asyncio.sleep(HABApp.config.CONFIG.openhab.ping.interval)

        except asyncio.CancelledError:
            pass
        except (OpenhabNotReadyYet, OpenhabDisconnectedError):
            pass


PLUGIN_PING = PingOpenhab.create_plugin()
