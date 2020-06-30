import logging
from typing import List

from HABApp.core.wrapper import ExceptionToHABApp

log = logging.getLogger('HABApp.openhab')


class PluginBase:
    IS_CONNECTED: bool = False

    @classmethod
    def create_plugin(cls):
        c = cls()
        assert c not in PLUGINS
        PLUGINS.append(c)

    def setup(self):
        raise NotImplementedError()

    def on_connect(self):
        raise NotImplementedError()

    def on_disconnect(self):
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
    for p in PLUGINS:
        with ExceptionToHABApp(log, ignore_exception=True):
            p.setup()
