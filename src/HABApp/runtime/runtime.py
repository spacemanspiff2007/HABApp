import asyncio
from pathlib import Path

import HABApp
import HABApp.config
import HABApp.core
import HABApp.mqtt.mqtt_connection
import HABApp.parameters.parameter_files
import HABApp.rule.interfaces._http
import HABApp.rule_manager
import HABApp.util
import eascheduler
from HABApp.core.asyncio import async_context
from HABApp.core.base.replace_dummy_objs import replace_dummy_objs
from HABApp.core.wrapper import process_exception
from HABApp.openhab import connection_logic as openhab_connection
from HABApp.runtime import shutdown


class Runtime:

    def __init__(self):
        self.config: HABApp.config.Config = None

        # Rule engine
        self.rule_manager: HABApp.rule_manager.RuleManager = None

        # Async Workers & shutdown callback
        shutdown.register_func(
            HABApp.core.impl.wrapped_function.wrapped_sync.stop_thread_pool, msg='Stopping thread pool')

    async def start(self, config_folder: Path):
        try:
            token = async_context.set('HABApp startup')

            # setup exception handler for the scheduler
            eascheduler.set_exception_handler(lambda x: process_exception('HABApp.scheduler', x))

            # Start Folder watcher!
            HABApp.core.files.watcher.start()

            # Load config
            HABApp.config.load_config(config_folder)

            # Todo: load this from config
            HABApp.core.impl.wrapped_function.create_thread_pool(10)

            # replace dummy objects
            # Todo: move this to plugin
            eb = HABApp.core.impl.EventBus()
            ir = HABApp.core.impl.ItemRegistry()
            objs = replace_dummy_objs(HABApp, HABApp.core.EventBus, eb)
            replace_dummy_objs(HABApp, HABApp.core.base.post_event, eb.post_event, replaced_objs=objs)
            replace_dummy_objs(HABApp, HABApp.core.Items, ir, replaced_objs=objs)
            replace_dummy_objs(HABApp, HABApp.core.base.get_item, ir.get_item, replaced_objs=objs)

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
