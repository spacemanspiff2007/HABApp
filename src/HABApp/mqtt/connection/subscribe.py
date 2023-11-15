from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

import HABApp
from HABApp.config import CONFIG
from HABApp.core.asyncio import run_func_from_async
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import uses_get_item, uses_item_registry, uses_post_event
from HABApp.core.lib import SingleTask
from HABApp.core.wrapper import process_exception
from HABApp.mqtt.connection.connection import MqttPlugin
from HABApp.mqtt.events import MqttValueChangeEvent, MqttValueUpdateEvent
from HABApp.mqtt.mqtt_payload import get_msg_payload

if TYPE_CHECKING:
    from HABApp.config.models.mqtt import QOS

SUBSCRIBE_CFG = CONFIG.mqtt.subscribe


class SubscriptionHandler(MqttPlugin):
    def __init__(self):
        super().__init__(task_name='MqttSubscribe')
        self.runtime_subs: dict[str, int] = {}
        self.subscribed_to: dict[str, int] = {}

        self.sub_task = SingleTask(self.apply_subscriptions, 'ApplySubscriptionsTask')

    async def interface_subscribe(self, topic_or_topics: str | Iterable[tuple[str, int | None]],
                                  qos: QOS | None = None):
        """
        Subscribe to a MQTT topic. Note that subscriptions made this way are volatile and will only remain until
        the next restart.

        :param topic_or_topics: MQTT topic or multiple topic qos pairs to subscribe to
        :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
        """

        if qos is None:
            qos = SUBSCRIBE_CFG.qos
        if not isinstance(topic_or_topics, str):
            for _t, _q in topic_or_topics:
                self.runtime_subs[_t] = _q if _q is not None else qos
        else:
            self.runtime_subs[topic_or_topics] = qos

        if self.plugin_connection.context is not None:
            await self.apply_subscriptions()

    async def interface_unsubscribe(self, topic_or_topics: str | Iterable[str]):
        """
        Unsubscribe from a MQTT topic

        :param topic_or_topics: MQTT topic
        """

        if isinstance(topic_or_topics, str):
            topic_or_topics = [topic_or_topics]

        for topic in topic_or_topics:
            self.runtime_subs.pop(topic, None)

        if self.plugin_connection.context is not None:
            await self.apply_subscriptions()

    def subscription_cfg_changed(self):
        if not self.plugin_connection.is_online:
            return None
        self.sub_task.start_if_not_running()

    async def unsubscribe(self, topics: list[str] | None):
        log = self.plugin_connection.log

        if (client := self.plugin_connection.context) is None:
            return None

        if topics is None:
            topics = sorted(set(self.runtime_subs) | set(self.subscribed_to))

        if not topics:
            return None

        log.debug('Unsubscribing from:')
        for topic in topics:
            log.debug(f' - "{topic:s}"')

        await client.unsubscribe(topics)

        for topic in topics:
            self.subscribed_to.pop(topic)

    async def apply_subscriptions(self):
        log = self.plugin_connection.log
        default_qos = SUBSCRIBE_CFG.qos

        client = self.plugin_connection.context
        assert client is not None

        target: dict[str, int] = {}

        # If our connection has errors we'll do a disconnect cycle anyway, so we don't even try to subscribe to anything
        # Unsubscribing has the corresponding handling, so we call that every time
        if not self.plugin_connection.has_errors:
            # subscription from config
            for topic, qos in CONFIG.mqtt.subscribe.topics:
                target[topic] = qos if qos is not None else default_qos
            # runtime subscriptions overwrite the subscriptions from the config file
            for topic, qos in self.runtime_subs.items():
                target[topic] = qos

        unsubscribe = []
        for sub_topic, sub_qos in sorted(self.subscribed_to.items()):
            if sub_topic not in target or target[sub_topic] != sub_qos:
                unsubscribe.append(sub_topic)

        await self.unsubscribe(unsubscribe)

        if subscribe := [(topic, qos) for topic, qos in target.items() if topic not in self.subscribed_to]:
            log.debug('Subscribing to:')
            for topic, qos in subscribe:
                log.debug(f' - "{topic}" (QoS {qos:d})')

            await client.subscribe(subscribe)

            for topic, qos in subscribe:
                self.subscribed_to[topic] = qos

        log.debug('Subscriptions successfully updated')

    async def on_connected(self):
        await super().on_connected()

        # Since we are freshly connected we have not yet subscribed to anything
        # We need to clear this here because in case of error it might still have the topics
        # from the last successful subscription in this dict
        self.subscribed_to.clear()

        self.sub_task.start_if_not_running()
        await self.sub_task.wait()

    async def on_disconnected(self):
        await super().on_disconnected()
        await self.sub_task.cancel_wait()

        # without errors, it's a graceful disconnect
        if not self.plugin_connection.has_errors:
            await self.unsubscribe(None)

    async def mqtt_task(self):
        client = self.plugin_connection.context
        assert client is not None

        async with client.messages() as messages:
            async for message in messages:

                try:
                    topic, payload = get_msg_payload(message)
                    if topic is None:
                        continue

                    msg_to_event(topic, payload, message.retain)
                except Exception as e:
                    process_exception('mqtt payload handling', e, logger=self.plugin_connection.log)


post_event = uses_post_event()
get_item = uses_get_item()
Items = uses_item_registry()


def msg_to_event(topic: str, payload: Any, retain: bool):

    _item = None    # type: HABApp.mqtt.items.MqttBaseItem | None
    try:
        _item = get_item(topic)   # type: HABApp.mqtt.items.MqttBaseItem
    except ItemNotFoundException:
        # only create items for if the message has the retain flag
        if retain:
            _item = Items.add_item(HABApp.mqtt.items.MqttItem(topic))

    # we don't have an item -> we process only the event
    if _item is None:
        post_event(topic, MqttValueUpdateEvent(topic, payload))
        return None

    # Remember state and update item before doing callbacks
    _old_state = _item.value
    _item.set_value(payload)

    post_event(topic, MqttValueUpdateEvent(topic, payload))
    if payload != _old_state:
        post_event(topic, MqttValueChangeEvent(topic, payload, _old_state))


SUBSCRIPTION_HANDLER = SubscriptionHandler()


async_subscribe = SUBSCRIPTION_HANDLER.interface_subscribe
async_unsubscribe = SUBSCRIPTION_HANDLER.interface_unsubscribe


def subscribe(topic_or_topics: str | Iterable[tuple[str, int | None]], qos: QOS | None = None):
    """
    Subscribe to a MQTT topic. Note that subscriptions made this way are volatile and will only remain until
    the next restart.

    :param topic_or_topics: MQTT topic or multiple topic qos pairs to subscribe to
    :param qos: QoS, can be 0, 1 or 2.  If not specified value from configuration file will be used.
    """
    run_func_from_async(async_subscribe(topic_or_topics, qos))


def unsubscribe(topic_or_topics: str | Iterable[str]):
    """
    Unsubscribe from a MQTT topic

    :param topic_or_topics: MQTT topic
    """
    run_func_from_async(async_subscribe(topic_or_topics))
