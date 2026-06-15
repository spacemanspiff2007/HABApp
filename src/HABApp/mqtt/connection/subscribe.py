from __future__ import annotations

from typing import TYPE_CHECKING, Final

from HABApp.core.lib.asyncio import AsyncioProvider
from HABApp.mqtt.connection.connection import MqttPlugin


if TYPE_CHECKING:

    from HABApp.config.models.mqtt import QOS
    from HABApp.config.models.mqtt import Subscribe as SubscribeConfig


class SubscriptionHandler(MqttPlugin):
    def __init__(self, subscribe_cfg: SubscribeConfig, asyncio_provider: AsyncioProvider) -> None:
        super().__init__()

        self._config: Final = subscribe_cfg

        self._subs_target: Final[dict[str, QOS]] = {}
        self._subscribed_to: Final[dict[str, QOS]] = {}

        self._sub_task: Final = asyncio_provider.create_single_task(self._apply_subscriptions, 'ApplySubscriptionsTask')

    async def on_connected(self) -> None:
        # Since we are freshly connected we have not yet subscribed to anything
        # We need to clear this here because in case of error it might still have the topics
        # from the last successful subscription in this dict
        self._subscribed_to.clear()

        self._sub_task.start_if_not_running()
        await self._sub_task.wait()

    async def on_disconnected(self) -> None:
        await self._sub_task.cancel_wait()

        # without errors, it's a graceful disconnect so we unsubscribe
        if not self.plugin_connection.has_errors:
            await self._do_unsubscribe(list(self._subscribed_to))

    def config_changed(self) -> None:
        if not self.plugin_connection.is_online:
            return None
        self._sub_task.start_if_not_running()
        return None

    def subscribe(self, topics: tuple[tuple[str, QOS | None], ...]) -> None:
        for topic, qos in topics:
            self._subs_target[topic] = qos if qos is not None else self._config.qos

        self.config_changed()

    def unsubscribe(self, topics: tuple[str, ...]) -> None:
        for topic in topics:
            self._subs_target.pop(topic, None)

        self.config_changed()

    async def _do_subscribe(self, topics: list[tuple[str, QOS]]) -> None:
        if not topics:
            return None

        if (client := self.plugin_connection.context) is None:
            raise RuntimeError()
        log = self.plugin_connection.log

        if len(topics) == 1:
            topic, qos = topics[0]
            log.debug(f'Subscribing to "{topic}" (QoS {qos:d})')
        else:
            log.debug('Subscribing to:')
            for topic, qos in sorted(topics):
                log.debug(f' - "{topic}" (QoS {qos:d})')

        await client.subscribe(topics)

        for topic, qos in topics:
            self._subscribed_to[topic] = qos
        return None

    async def _do_unsubscribe(self, topics: list[str]) -> None:
        if not topics:
            return None

        if (client := self.plugin_connection.context) is None:
            return None
        log = self.plugin_connection.log

        if len(topics) == 1:
            log.debug(f'Unsubscribing from "{topics[0]}"')
        else:
            log.debug('Unsubscribing from:')
            for topic in sorted(topics):
                log.debug(f' - "{topic}"')

        await client.unsubscribe(topics)

        for topic in topics:
            self._subscribed_to.pop(topic)
        return None

    async def _apply_subscriptions(self) -> None:
        has_changed: bool = False

        # If our connection has errors we'll do a disconnect cycle anyway
        # so we don't even try to subscribe to anything
        while not self.plugin_connection.has_errors:

            target: dict[str, QOS] = dict(self._config.get_topic_qos())
            target.update(self._subs_target)

            if target == self._subscribed_to:
                break
            has_changed = True

            to_remove = list(frozenset(self._subscribed_to) - frozenset(target))

            to_add: list[tuple[str, QOS]] = []
            for topic, qos in target.items():
                if (subscribed_qos := self._subscribed_to.get(topic)) is None or subscribed_qos != qos:
                    to_add.append((topic, qos))

            if not self.plugin_connection.has_errors:
                await self._do_unsubscribe(to_remove)

            if not self.plugin_connection.has_errors:
                await self._do_subscribe(to_add)

        if has_changed:
            self.plugin_connection.log.debug('Subscriptions successfully updated')
