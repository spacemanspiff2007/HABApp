import asyncio
import logging
from typing import List, Optional

from HABApp.core.wrapper import ExceptionToHABApp

log = logging.getLogger('HABApp.openhab.plugin')


class PluginBase:
    IS_CONNECTED: bool = False

    @classmethod
    def create_plugin(cls):
        c = cls()
        assert c not in PLUGINS
        PLUGINS.append(c)
        return c

    def setup(self):
        raise NotImplementedError()

    def on_connect(self):
        raise NotImplementedError()

    def on_disconnect(self):
        raise NotImplementedError()


class OnConnectPlugin(PluginBase):
    """Plugin that runs a function on connect"""
    def __init__(self):
        super().__init__()
        self.fut: Optional[asyncio.Future] = None

    def setup(self):
        pass

    def on_connect(self):
        self.fut = asyncio.create_task(self.on_connect_function())

    def on_disconnect(self):
        if self.fut is not None:
            self.fut.cancel()
            self.fut = None

    async def on_connect_function(self):
        raise NotImplementedError()


PLUGINS: List[PluginBase] = []


def on_connect():
    PluginBase.IS_CONNECTED = True
    for p in PLUGINS:
        with ExceptionToHABApp(log, ignore_exception=True):
            p.on_connect()


def on_disconnect():
    PluginBase.IS_CONNECTED = False
    for p in PLUGINS:
        with ExceptionToHABApp(log, ignore_exception=True):
            p.on_disconnect()


def setup_plugins():
    log.debug('Starting setup')
    for p in PLUGINS:
        with ExceptionToHABApp(log, ignore_exception=True):
            p.setup()
            log.debug(f'Setup {p.__class__.__name__} complete')
