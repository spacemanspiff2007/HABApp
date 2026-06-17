from __future__ import annotations

import logging
from asyncio import sleep
from time import monotonic
from typing import Final

import HABApp.openhab.events
from HABApp.config import CONFIG
from HABApp.core.connections import BaseConnectionPlugin
from HABApp.core.internals import EventBus, ExecutorFactory, ItemRegistry
from HABApp.core.lib.asyncio import AsyncioProvider
from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.openhab.connection.connection import OpenhabConnection
from HABApp.openhab.connection.handler import OpenHabAsyncInterface


PING_CONFIG: Final = CONFIG.openhab.ping

log = logging.getLogger('HABApp.openhab.items')


class PingPlugin(BaseConnectionPlugin[OpenhabConnection]):

    def __init__(self, name: str | None = None, *,
                 event_bus: EventBus, item_registry: ItemRegistry,
                 asyncio_provider: AsyncioProvider, interface: OpenHabAsyncInterface) -> None:
        super().__init__(name)
        self._event_bus: Final = event_bus
        self._item_registry: Final = item_registry
        self._interface: Final = interface
        self.task: Final = asyncio_provider.create_single_task(self.ping_worker, 'OhQueueWorker')

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

        executor_factory = await HABAPP_PROVIDER.get(ExecutorFactory)

        self.listener = listener = HABApp.core.internals.EventBusListener(
            HABApp.config.CONFIG.openhab.ping.item,
            executor_factory.create(self.ping_received),
            HABApp.core.events.EventFilter(HABApp.openhab.events.ItemStateUpdatedEvent)
        )
        self._event_bus.add_listener(listener)

        self.task.start()

    async def on_disconnected(self) -> None:
        await self.task.cancel_wait()

        if (listener := self.listener) is not None:
            self.listener = None
            listener.cancel()

    async def ping_received(self, event: HABApp.openhab.events.ItemStateEvent) -> None:
        value = event.value
        if value != self.sent_value:
            return None

        # If we are queued up it's possible that we receive multiple pings
        # Then we only take the first one
        if self.next_value is None:
            self.next_value = round((monotonic() - self.timestamp_sent) * 1000, 1)
        return None

    async def ping_worker(self) -> None:
        try:
            log.debug('Ping started')

            item_name = PING_CONFIG.item

            if not (send_ping := self._item_registry.item_exists(item_name)):
                log.warning(f'Number item "{item_name:s}" does not exist!')

            while True:
                self.sent_value = self.next_value
                self.next_value = None
                self.timestamp_sent = monotonic()

                if send_ping:
                    self._interface.post_update(
                        item_name,
                        f'{self.sent_value:.1f}' if self.sent_value is not None else None,
                        transport='http'
                    )
                else:
                    send_ping = self._item_registry.item_exists(item_name)

                await sleep(PING_CONFIG.interval)

        except Exception as e:
            self.plugin_connection.process_exception(e, self.ping_worker)
        finally:
            log.debug('Ping stopped')
