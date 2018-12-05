import asyncio, logging
import concurrent.futures

import HABApp.util
import HABApp.config
import HABApp.core
import HABApp.rule_manager

class Runtime:
    def __init__(self, config_folder):

        self.shutdown = HABApp.util.CallbackHelper('Shutdown', logging.getLogger('HABApp.Shutdown'))

        self.config     = HABApp.config.Config(config_folder=config_folder, shutdown_helper = self.shutdown)
        self.events     = HABApp.core.EventBus(self)
        self.connection = HABApp.core.Connection(self)
        self.all_items  = HABApp.core.Items(self)

        self.workers = concurrent.futures.ThreadPoolExecutor(10, 'HabApp_')

        self.rule_manager = HABApp.rule_manager.RuleManager(self)

        self.loop = asyncio.get_event_loop()

    @HABApp.util.PrintException
    def get_async(self):
        return asyncio.gather(
            self.connection.get_async(),
            self.rule_manager.get_async(),
        )