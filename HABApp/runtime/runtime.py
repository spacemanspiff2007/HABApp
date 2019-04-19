import asyncio

import HABApp.config
import HABApp.core
import HABApp.rule_manager
import HABApp.util

from .folder_watcher import FolderWatcher
from .shutdown_helper import ShutdownHelper


class Runtime:
    def __init__(self, config_folder):

        self.loop = asyncio.get_event_loop()

        self.shutdown = ShutdownHelper()

        self.folder_watcher = FolderWatcher()
        self.folder_watcher.start(self.shutdown)

        self.config = HABApp.config.Config(self, config_folder=config_folder)

        self.async_http = HABApp.async_http.AsyncHttpConnection()

        # OpenHAB
        self.openhab_connection = HABApp.openhab.OpenhabConnection(self)

        # MQTT
        self.mqtt_connection = HABApp.mqtt.MqttConnection(self.config.mqtt, self.shutdown)
        self.mqtt_connection.connect()

        self.rule_manager = HABApp.rule_manager.RuleManager(self)
        self.rule_params = HABApp.rule_manager.RuleParameters(self.config, self.folder_watcher)


        # Shutdown workers
        self.shutdown.register_func(HABApp.core.WrappedFunction._WORKERS.shutdown)

    @HABApp.util.PrintException
    def get_async(self):
        return asyncio.gather(
            self.openhab_connection.start(),
            self.rule_manager.get_async(),
        )
