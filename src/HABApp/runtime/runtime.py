import asyncio
from pathlib import Path

import eascheduler

import HABApp
import HABApp.config
import HABApp.core
import HABApp.mqtt.connection as mqtt_connection
import HABApp.parameters.parameter_files
import HABApp.rule_manager
import HABApp.util
from HABApp.config.models import ApplicationConfig
from HABApp.core import Connections, shutdown
from HABApp.core.files import FileManager
from HABApp.core.internals import setup_internals
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.core.wrapper import process_exception
from HABApp.openhab import connection as openhab_connection
from HABApp.rule_manager import RuleManager


class Runtime:

    async def start(self, config_folder: Path) -> None:
        try:
            # shutdown setup
            shutdown.register(Connections.on_application_shutdown, msg='Shutting down connections')

            # setup exception handler for the scheduler
            eascheduler.set_exception_handler(lambda x: process_exception('HABApp.scheduler', x))

            # replace proxy objects
            ir = await HABAPP_PROVIDER.get(HABApp.core.internals.ItemRegistry)
            eb = await HABAPP_PROVIDER.get(HABApp.core.internals.EventBus)
            file_manager = await HABAPP_PROVIDER.get(HABApp.core.files.FileManager)

            setup_internals(ir, eb, file_manager)
            assert isinstance(HABApp.core.Items, ConstProxyObj)
            HABApp.core.Items = ir
            assert isinstance(HABApp.core.EventBus, ConstProxyObj)
            HABApp.core.EventBus = eb


            # Load config
            HABApp.config.setup_habapp_configuration(config_folder)

            # Connection setup
            openhab_connection.setup()
            mqtt_connection.setup()

            # File loader setup
            # Parameter Files
            await HABApp.parameters.parameter_files.setup_param_files(
                await HABAPP_PROVIDER.get(ApplicationConfig),
                await HABAPP_PROVIDER.get(FileManager)
            )

            # Rule engine
            rule_manager = await HABAPP_PROVIDER.get(RuleManager)

            Connections.application_startup_complete()

            await rule_manager.load_rules_on_startup()


        except HABApp.config.InvalidConfigError:
            shutdown.request()
        except Exception as e:
            process_exception('Runtime.start', e)
            await asyncio.sleep(1)  # Sleep so we can do a graceful shutdown
            shutdown.request()
