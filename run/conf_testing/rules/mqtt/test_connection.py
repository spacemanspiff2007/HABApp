import asyncio

from HABAppTests import EventWaiter, TestBaseRule, get_random_string

import HABApp
from HABApp.core.connections import Connections, ConnectionStatus
from HABApp.core.events import ValueUpdateEventFilter
from HABApp.mqtt import interface_async


class TestMQTTConnection(TestBaseRule):
    """This rule is testing MQTT by posting values and checking the events"""

    def __init__(self) -> None:
        super().__init__()

        self.config.skip_on_failure = True

        self.add_test('MQTT subscribe', self.test_mqtt_subscribe)
        self.add_test('MQTT async subscribe', self.test_mqtt_async_subscribe)

        self.add_test('MQTT item creation', self.test_mqtt_item_creation)

        self.add_test('MQTT sync subscribed', self.test_sync_subscribed_event)
        self.add_test('MQTT async subscribed', self.test_async_subscribed_event)

        self.topic_sync = 'test/subscribe_topic_sync'
        self.topic_async = 'test/subscribe_topic_async'

    def test_sync_subscribed_event(self) -> None:
        data = get_random_string(5)
        with EventWaiter(self.topic_sync, ValueUpdateEventFilter()) as waiter:
            self.mqtt.publish(self.topic_sync, data)
            waiter.wait_for_event(value=data)

    def test_mqtt_subscribe(self) -> None:
        self.mqtt.subscribe(self.topic_sync)
        self.test_sync_subscribed_event()

    async def test_async_subscribed_event(self) -> None:
        data = get_random_string(5)
        with EventWaiter(self.topic_async, ValueUpdateEventFilter()) as waiter:
            self.mqtt.publish(self.topic_async, data)
            await waiter.async_wait_for_event(value=data)

    async def test_mqtt_async_subscribe(self) -> None:
        await interface_async.async_subscribe(self.topic_async)
        await self.test_async_subscribed_event()

    async def test_mqtt_item_creation(self) -> None:
        topic = 'mqtt/item/creation'
        assert HABApp.core.Items.item_exists(topic) is False

        self.mqtt.publish(topic, 'asdf')
        await asyncio.sleep(0.1)
        assert HABApp.core.Items.item_exists(topic) is False

        # We create the item only on retain
        self.mqtt.publish(topic, 'asdf', retain=True)
        await asyncio.sleep(0.2)

        await self.trigger_reconnect()

        await asyncio.sleep(0.2)
        connection = Connections.get('mqtt')
        while not connection.is_online:
            await asyncio.sleep(0.2)

        assert HABApp.core.Items.item_exists(topic) is True

        HABApp.core.Items.pop_item(topic)

    async def trigger_reconnect(self) -> None:
        connection = Connections.get('mqtt')
        connection.status._set_manual(ConnectionStatus.DISCONNECTED)
        connection.advance_status_task.start_if_not_running()


TestMQTTConnection()
