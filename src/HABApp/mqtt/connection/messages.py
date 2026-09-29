from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import HABApp
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.lib.asyncio import AsyncioProvider
from HABApp.core.wrapper import process_exception
from HABApp.mqtt.connection.connection import MqttTaskPlugin
from HABApp.mqtt.events import MqttValueChangeEvent, MqttValueUpdateEvent
from HABApp.mqtt.mqtt_payload import get_msg_payload


if TYPE_CHECKING:
    from HABApp.core.internals import EventBus, ItemRegistry
    from HABApp.mqtt import MqttInterface


class MessagesHandler(MqttTaskPlugin):
    def __init__(self, interface: MqttInterface, event_bus: EventBus, item_registry: ItemRegistry,
                 asyncio_provider: AsyncioProvider) -> None:
        super().__init__(task_name='MqttMessages', asyncio_provider=asyncio_provider)
        self._interface: Final = interface
        self._event_bus: Final = event_bus
        self._item_registry: Final = item_registry

    async def mqtt_task(self) -> None:
        client = self.plugin_connection.context
        assert client is not None

        async for message in client.messages:
            try:
                topic, payload = get_msg_payload(message)
                if topic is None:
                    continue

                self.msg_to_event(topic, payload, message.retain)
            except Exception as e:
                process_exception('mqtt payload handling', e, logger=self.plugin_connection.log)

    def msg_to_event(self, topic: str, payload: Any, retain: bool) -> None:

        _item = None    # type: HABApp.mqtt.items.MqttBaseItem | None
        try:
            _item = self._item_registry.get_item(topic)   # type: HABApp.mqtt.items.MqttBaseItem
        except ItemNotFoundException:
            # only create items for if the message has the retain flag
            if retain:
                _item = self._item_registry.add_item(
                    HABApp.mqtt.items.MqttItem(topic, interface=self._interface, event_bus=self._event_bus)
                )

        # we don't have an item -> we process only the event
        if _item is None:
            self._event_bus.post_event(topic, MqttValueUpdateEvent(topic, payload))
            return None

        # Remember state and update item before doing callbacks
        _old_state = _item.value
        _item.set_value(payload)

        self._event_bus.post_event(topic, MqttValueUpdateEvent(topic, payload))
        if payload != _old_state:
            self._event_bus.post_event(topic, MqttValueChangeEvent(topic, payload, _old_state))
        return None
