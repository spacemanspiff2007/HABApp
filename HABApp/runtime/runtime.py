import asyncio

import HABApp.config
import HABApp.core
import HABApp.rule_manager
import HABApp.util

from .folder_watcher import FolderWatcher
from .shutdown_helper import ShutdownHelper


class Runtime:

    def __init__(self):

        self.loop = asyncio.get_event_loop()

        self.shutdown = ShutdownHelper()

        self.folder_watcher: FolderWatcher = FolderWatcher()

        self.config: HABApp.config.Config = None

        self.async_http: HABApp.rule.interfaces.AsyncHttpConnection = HABApp.rule.interfaces.AsyncHttpConnection()

        # OpenHAB
        self.openhab_connection: HABApp.openhab.OpenhabConnection = None

        # MQTT
        self.mqtt_connection: HABApp.mqtt.MqttConnection = None

        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None
        self.rule_params: HABApp.rule_manager.RuleParameters = None

        # Shutdown workers
        self.shutdown.register_func(HABApp.core.WrappedFunction._WORKERS.shutdown)

    def load_config(self, config_folder):

        # Start Folder watcher!
        self.folder_watcher.start(self.shutdown)

        self.config = HABApp.config.Config(self, config_folder=config_folder)

        # OpenHAB
        self.openhab_connection = HABApp.openhab.OpenhabConnection(self.config, self.shutdown)

        # MQTT
        self.mqtt_connection = HABApp.mqtt.MqttConnection(self.config.mqtt, self.shutdown)
        self.mqtt_connection.connect()

        # Rule engine
        self.rule_manager = HABApp.rule_manager.RuleManager(self)
        self.rule_params = HABApp.rule_manager.RuleParameters(self.config, self.folder_watcher)

    @HABApp.util.PrintException
    def get_async(self):
        return asyncio.gather(
            self.async_http.create_client(),
            self.openhab_connection.start(),
            self.rule_manager.get_async(),
        )
