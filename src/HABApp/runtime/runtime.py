from pathlib import Path

import HABApp.config
import HABApp.core
import HABApp.mqtt.mqtt_connection
import HABApp.parameters.parameter_files
import HABApp.rule_manager
import HABApp.util
import eascheduler
from HABApp.core.wrapper import process_exception
from HABApp.openhab import connection_logic as openhab_connection
from HABApp.runtime import shutdown


class Runtime:

    def __init__(self):
        self.config: HABApp.config.Config = None

        self.async_http: HABApp.rule.interfaces.AsyncHttpConnection = HABApp.rule.interfaces.AsyncHttpConnection()

        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None

        # Async Workers & shutdown callback
        # Setup scheduler
        eascheduler.schedulers.ThreadSafeAsyncScheduler.LOOP = HABApp.core.const.loop
        HABApp.core.WrappedFunction._EVENT_LOOP = HABApp.core.const.loop
        shutdown.register_func(HABApp.core.WrappedFunction._WORKERS.shutdown, msg='Stopping workers')

    @HABApp.core.wrapper.log_exception
    async def start(self, config_folder: Path):
        # setup exception handler for the scheduler
        eascheduler.set_exception_handler(lambda x: process_exception('HABApp.scheduler', x))

        # Start Folder watcher!
        HABApp.core.files.watcher.start()

        self.config_loader = HABApp.config.HABAppConfigLoader(config_folder)

        await HABApp.core.files.setup()

        # MQTT
        HABApp.mqtt.mqtt_connection.setup()
        HABApp.mqtt.mqtt_connection.connect()

        # openhab
        openhab_connection.setup()

        # Parameter Files
        await HABApp.parameters.parameter_files.setup_param_files()

        # Rule engine
        self.rule_manager = HABApp.rule_manager.RuleManager(self)
        await self.rule_manager.setup()

        await self.async_http.create_client()
        await openhab_connection.start()

        shutdown.register_func(HABApp.core.const.loop.stop, msg='Stopping asyncio loop')
