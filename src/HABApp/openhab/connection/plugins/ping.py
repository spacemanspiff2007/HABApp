from __future__ import annotations

import logging
from asyncio import sleep
from time import monotonic
from typing import Final

import HABApp.openhab.events
from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import uses_item_registry, uses_event_bus
from HABApp.core.lib import SingleTask
from HABApp.openhab.connection.connection import OpenhabConnection

PING_CONFIG: Final = CONFIG.openhab.ping

log = logging.getLogger('HABApp.openhab.items')
Items = uses_item_registry()
EventBus = uses_event_bus()


class PingPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None):
        super().__init__(name)
        self.task: Final = SingleTask(self.ping_worker, 'OhQueueWorker')

        self.sent_value: float | None = None
        self.next_value: float | None = None
        self.timestamp_sent: float | None = None

        self.listener: HABApp.core.internals.EventBusListener | None = None

    async def on_connected(self):
        if not PING_CONFIG.enabled:
            return None

        self.sent_value = None
        self.next_value = None
        self.timestamp_sent = None

        self.listener = HABApp.core.internals.EventBusListener(
            HABApp.config.CONFIG.openhab.ping.item,
            HABApp.core.internals.wrap_func(self.ping_received),
            HABApp.core.events.EventFilter(HABApp.openhab.events.ItemStateUpdatedEvent)
        )
        EventBus.add_listener(self.listener)

        self.task.start()

    async def on_disconnected(self):
        await self.task.cancel_wait()

        if self.listener is not None:
            self.listener.cancel()
            self.listener = None

    async def ping_received(self, event: HABApp.openhab.events.ItemStateEvent):
        value = event.value
        if value != self.sent_value:
            return None

        # If we are queued up it's possible that we receive multiple pings
        # Then we only take the first one
        if self.next_value is None:
            self.next_value = round((monotonic() - self.timestamp_sent) * 1000, 1)

    async def ping_worker(self):
        try:
            log.debug('Ping started')

            item_name = PING_CONFIG.item

            if not (send_ping := Items.item_exists(item_name)):
                log.warning(f'Number item "{item_name:s}" does not exist!')

            while True:
                self.sent_value = self.next_value
                self.next_value = None
                self.timestamp_sent = monotonic()

                if send_ping:
                    HABApp.openhab.interface_async.async_post_update(
                        item_name,
                        f'{self.sent_value:.1f}' if self.sent_value is not None else None
                    )
                else:
                    send_ping = Items.item_exists(item_name)

                await sleep(PING_CONFIG.interval)

        except Exception as e:
            self.plugin_connection.process_exception(e, self.ping_worker)
        finally:
            log.debug('Ping stopped')
