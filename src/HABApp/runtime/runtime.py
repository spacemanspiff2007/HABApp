import asyncio
import logging
import warnings
from pathlib import Path

import eascheduler

import HABApp
import HABApp.config
import HABApp.core
import HABApp.parameters.parameter_files
import HABApp.rule_manager
import HABApp.util
from HABApp.config.models import ApplicationConfig
from HABApp.core import shutdown
from HABApp.core.connections import ConnectionManager
from HABApp.core.files import FileManager
from HABApp.core.internals import setup_internals
from HABApp.core.internals.proxy import ConstProxyObj
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.core.wrapper import process_exception
from HABApp.mqtt.connection.connection import MqttConnection
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.rule_manager import RuleManager


log = logging.getLogger('HABApp.Warnings')


# Func to log deprecation warnings
def send_warnings_to_log(message, category, filename, lineno, file=None, line=None) -> None:  # noqa: PLR0913
    log.warning(f'{filename}:{lineno}: {category.__name__}: {message}')
    return


# Setup deprecation warnings
warnings.simplefilter('default')
warnings.showwarning = send_warnings_to_log


class Runtime:

    async def start(self, config_folder: Path) -> None:
        try:

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
            await HABApp.config.setup_habapp_configuration(config_folder)

            # Connection setup
            await HABAPP_PROVIDER.get(OpenhabConnection)
            await HABAPP_PROVIDER.get(MqttConnection)

            # File loader setup
            # Parameter Files
            await HABApp.parameters.parameter_files.setup_param_files(
                await HABAPP_PROVIDER.get(ApplicationConfig),
                await HABAPP_PROVIDER.get(FileManager)
            )

            # Rule engine
            rule_manager = await HABAPP_PROVIDER.get(RuleManager)

            mgr = await HABAPP_PROVIDER.get(ConnectionManager)
            mgr.application_startup_complete()

            await rule_manager.load_rules_on_startup()


        except HABApp.config.InvalidConfigError:
            shutdown.request()
        except Exception as e:
            process_exception('Runtime.start', e)
            await asyncio.sleep(1)  # Sleep so we can do a graceful shutdown
            shutdown.request()
