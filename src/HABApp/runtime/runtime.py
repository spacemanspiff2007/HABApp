import asyncio
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
from HABApp.core.context import async_context

import HABApp.rule.interfaces._http


class Runtime:

    def __init__(self):
        self.config: HABApp.config.Config = None

        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None

        # Async Workers & shutdown callback
        shutdown.register_func(HABApp.core.WrappedFunction._WORKERS.shutdown, msg='Stopping workers')

    async def start(self, config_folder: Path):
        try:
            token = async_context.set('HABApp startup')

            # setup exception handler for the scheduler
            eascheduler.set_exception_handler(lambda x: process_exception('HABApp.scheduler', x))

            # Start Folder watcher!
            HABApp.core.files.watcher.start()

            # Load config
            HABApp.config.load_config(config_folder)

            await HABApp.core.files.setup()

            # generic HTTP
            await HABApp.rule.interfaces._http.create_client()

            # openhab
            openhab_connection.setup()

            # Parameter Files
            await HABApp.parameters.parameter_files.setup_param_files()

            # Rule engine
            self.rule_manager = HABApp.rule_manager.RuleManager(self)
            await self.rule_manager.setup()

            # MQTT
            HABApp.mqtt.mqtt_connection.setup()
            HABApp.mqtt.mqtt_connection.connect()

            await openhab_connection.start()

            shutdown.register_func(HABApp.core.const.loop.stop, msg='Stopping asyncio loop')

            async_context.reset(token)

        except HABApp.config.InvalidConfigError:
            shutdown.request_shutdown()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            process_exception('Runtime.start', e)
            await asyncio.sleep(1)  # Sleep so we can do a graceful shutdown
            shutdown.request_shutdown()
