import asyncio
from pathlib import Path

import HABApp.config
import HABApp.core
import HABApp.rule_manager
import HABApp.util
import HABApp.parameters.parameter_files

from .folder_watcher import FolderWatcher
from .shutdown_helper import ShutdownHelper
from HABApp.config import CONFIG


class Runtime:

    def __init__(self):
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

        # Async Workers & shutdown callback
        HABApp.core.WrappedFunction._EVENT_LOOP = HABApp.core.const.loop
        self.shutdown.register_func(HABApp.core.WrappedFunction._WORKERS.shutdown)

    def startup(self, config_folder: Path):

        # Start Folder watcher!
        self.folder_watcher.start(self.shutdown)

        self.config_loader = HABApp.config.HABAppConfigLoader(config_folder)

        # OpenHAB
        self.openhab_connection = HABApp.openhab.OpenhabConnection(HABApp.config.CONFIG.openhab, self.shutdown)

        # MQTT
        self.mqtt_connection = HABApp.mqtt.MqttConnection(HABApp.config.CONFIG.mqtt, self.shutdown)
        self.mqtt_connection.connect()

        # Parameter Files
        params_enabled = HABApp.parameters.parameter_files.setup_param_files()

        # Rule engine
        self.rule_manager = HABApp.rule_manager.RuleManager(self)

        # watch folders config
        self.folder_watcher.watch_folder(
            folder=config_folder,
            file_ending='.yml',
            target_func=self.config_loader.on_file_event
        )

        # folder watcher rules
        self.folder_watcher.watch_folder_habapp_events(
            folder=CONFIG.directories.rules, file_ending='.py',
            habapp_topic=HABApp.core.const.topics.RULES, watch_subfolders=True
        )

        # watch parameter files
        if params_enabled:
            param_watcher = self.folder_watcher.watch_folder_habapp_events(
                folder=HABApp.CONFIG.directories.param, file_ending='.yml',
                habapp_topic=HABApp.core.const.topics.PARAM, watch_subfolders=True
            )
            # load all param files through the worker
            HABApp.core.WrappedFunction(param_watcher.trigger_load_for_all_files, name='Load all parameter files').run()

        # watch folders for manual config
        if CONFIG.directories.config.is_dir():
            self.folder_watcher.watch_folder(
                folder=CONFIG.directories.config,
                file_ending='.yml',
                target_func=lambda x: asyncio.run_coroutine_threadsafe(
                    self.openhab_connection.update_thing_config(x), HABApp.core.const.loop
                )
            )

    @HABApp.core.wrapper.log_exception
    def get_async(self):
        return asyncio.gather(
            self.async_http.create_client(HABApp.core.const.loop),
            self.openhab_connection.start(),
            self.rule_manager.get_async(),
        )
