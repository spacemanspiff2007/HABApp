import asyncio
from pathlib import Path

import HABApp
import HABApp.config
import HABApp.core
import HABApp.parameters.parameter_files
import HABApp.rule.interfaces._http
import HABApp.rule_manager
from HABApp.core import Connections
import HABApp.util
import eascheduler
from HABApp.core.asyncio import async_context
from HABApp.core.internals import setup_internals
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.wrapper import process_exception
import HABApp.mqtt.connection as mqtt_connection
from HABApp.openhab import connection as openhab_connection
from HABApp.runtime import shutdown



class Runtime:

    def __init__(self):
        self.config: HABApp.config.Config = None

        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None

    async def start(self, config_folder: Path):
        try:
            token = async_context.set('HABApp startup')

            # shutdown setup
            shutdown.register_func(Connections.on_application_shutdown, msg='Shutting down connections')

            # setup exception handler for the scheduler
            eascheduler.set_exception_handler(lambda x: process_exception('HABApp.scheduler', x))

            # Start Folder watcher!
            HABApp.core.files.watcher.start()

            # Load config
            HABApp.config.load_config(config_folder)

            # replace proxy objects
            ir = HABApp.core.internals.ItemRegistry()
            eb = HABApp.core.internals.EventBus()
            setup_internals(ir, eb)
            assert isinstance(HABApp.core.Items, ConstProxyObj)
            HABApp.core.Items = ir
            assert isinstance(HABApp.core.EventBus, ConstProxyObj)
            HABApp.core.EventBus = eb

            await HABApp.core.files.setup()

            # generic HTTP
            await HABApp.rule.interfaces._http.create_client()

            # Connection setup
            openhab_connection.setup()
            mqtt_connection.setup()

            # File loader setup
            # Parameter Files
            await HABApp.parameters.parameter_files.setup_param_files()

            # Rule engine
            self.rule_manager = HABApp.rule_manager.RuleManager(self)
            await self.rule_manager.setup()

            Connections.application_startup_complete()

            async_context.reset(token)

        except HABApp.config.InvalidConfigError:
            shutdown.request_shutdown()
        except Exception as e:
            process_exception('Runtime.start', e)
            await asyncio.sleep(1)  # Sleep so we can do a graceful shutdown
            shutdown.request_shutdown()
