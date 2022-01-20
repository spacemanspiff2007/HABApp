from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events.filter.event import TypeBoundEventFilter
from HABApp.mqtt.events import MqttValueChangeEvent, MqttValueUpdateEvent


class MqttValueUpdateEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING):
        super().__init__(MqttValueUpdateEvent, value=value)


class MqttValueChangeEventFilter(TypeBoundEventFilter):
    def __init__(self, value: Any = MISSING, old_value: Any = MISSING):
        super().__init__(MqttValueChangeEvent, value=value, old_value=old_value)
