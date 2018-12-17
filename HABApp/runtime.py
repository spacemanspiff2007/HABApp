import asyncio
import logging

import HABApp.config
import HABApp.core
import HABApp.rule_manager
import HABApp.util


class Runtime:
    def __init__(self, config_folder):

        self.shutdown = HABApp.util.CallbackHelper('Shutdown', logging.getLogger('HABApp.Shutdown'))

        self.config = HABApp.config.Config(config_folder=config_folder, shutdown_helper=self.shutdown)

        # OpenHAB
        self.openhab_connection = HABApp.openhab.Connection(self)

        # MQTT
        self.mqtt_connection = HABApp.mqtt.MqttConnection(self)
        self.shutdown.register_func(self.mqtt_connection.disconnect)
        self.mqtt_connection.connect()

        self.rule_manager = HABApp.rule_manager.RuleManager(self)

        self.loop = asyncio.get_event_loop()

    @HABApp.util.PrintException
    def get_async(self):
        return asyncio.gather(
            self.openhab_connection.get_async(),
            self.rule_manager.get_async(),
        )
