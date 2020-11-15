from typing import Optional

import HABApp
import asyncio
import logging
import time
from HABApp.core.wrapper import log_exception
from ._plugin import PluginBase
from HABApp.openhab.exceptions import OpenhabNotReadyYet, OpenhabDisconnectedError

log = logging.getLogger('HABApp.openhab.ping')


class PingOpenhab(PluginBase):
    def __init__(self):
        self.__ping_received: float = 0
        self.__ping_value: Optional[float] = 0

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

        self.__ping_received = 0
        self.__ping_value = 0
        log.debug('Ping stopped')

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

    async def ping_received(self, event: HABApp.openhab.events.ItemStateEvent):
        value = event.value
        self.__ping_received = time.time()
        self.__ping_value = None if value is None else round(value, 2)

    @log_exception
    async def async_ping(self):
        await asyncio.sleep(3)

        sent: Optional[float] = time.time()
        value: Optional[float] = None

        log.debug('Ping started')
        try:
            while True:
                if self.__ping_value == value:
                    value = round((self.__ping_received - sent) * 1000, 2)
                else:
                    value = None

                await HABApp.openhab.interface_async.async_post_update(
                    HABApp.config.CONFIG.openhab.ping.item,
                    f'{value:.1f}' if value is not None else None
                )
                sent = time.time()

                await asyncio.sleep(HABApp.config.CONFIG.openhab.ping.interval)

        except (OpenhabNotReadyYet, OpenhabDisconnectedError):
            pass


PLUGIN_PING = PingOpenhab.create_plugin()
