from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import HABApp
from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import uses_get_item, uses_item_registry, uses_post_event
from HABApp.core.wrapper import process_exception
from HABApp.mqtt.connection.connection import MqttTaskPlugin
from HABApp.mqtt.events import MqttValueChangeEvent, MqttValueUpdateEvent
from HABApp.mqtt.mqtt_payload import get_msg_payload


if TYPE_CHECKING:
    from HABApp.mqtt import MqttInterface


class MessagesHandler(MqttTaskPlugin):
    def __init__(self, interface: MqttInterface) -> None:
        super().__init__(task_name='MqttMessages')
        self._interface: Final = interface

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
            _item = get_item(topic)   # type: HABApp.mqtt.items.MqttBaseItem
        except ItemNotFoundException:
            # only create items for if the message has the retain flag
            if retain:
                _item = Items.add_item(HABApp.mqtt.items.MqttItem(topic, interface=self._interface))

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
        return None


post_event = uses_post_event()
get_item = uses_get_item()
Items = uses_item_registry()
