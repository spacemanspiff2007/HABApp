import asyncio
from pathlib import Path

import HABApp.config
import HABApp.core
import HABApp.mqtt.mqtt_connection
import HABApp.parameters.parameter_files
import HABApp.rule_manager
import HABApp.util
from HABApp.openhab import connection_logic as openhab_connection
from .shutdown_helper import ShutdownHelper


class Runtime:

    def __init__(self):
        self.shutdown = ShutdownHelper()

        self.config: HABApp.config.Config = None

        self.async_http: HABApp.rule.interfaces.AsyncHttpConnection = HABApp.rule.interfaces.AsyncHttpConnection()

        # OpenHAB
        self.openhab_connection: HABApp.openhab.OpenhabConnection = None

        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None

        # Async Workers & shutdown callback
        HABApp.core.WrappedFunction._EVENT_LOOP = HABApp.core.const.loop
        self.shutdown.register_func(HABApp.core.WrappedFunction._WORKERS.shutdown)

    def startup(self, config_folder: Path):

        # Start Folder watcher!
        HABApp.core.files.watcher.start(self.shutdown)

        self.config_loader = HABApp.config.HABAppConfigLoader(config_folder)

        # MQTT
        HABApp.mqtt.mqtt_connection.setup(self.shutdown)
        HABApp.mqtt.mqtt_connection.connect()

        # openhab
        openhab_connection.setup(self.shutdown)

        # Parameter Files
        HABApp.parameters.parameter_files.setup_param_files()

        # Rule engine
        self.rule_manager = HABApp.rule_manager.RuleManager(self)
        self.rule_manager.setup()


    @HABApp.core.wrapper.log_exception
    def get_async(self):
        return asyncio.gather(
            self.async_http.create_client(),
            openhab_connection.start(),
            self.rule_manager.get_async(),
        )
