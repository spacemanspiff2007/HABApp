from typing import Any

from HABApp.core.const import MISSING
from HABApp.core.events import EventFilter
from . import MqttValueChangeEvent, MqttValueUpdateEvent


class MqttValueUpdateEventFilter(EventFilter):
    def __init__(self, *, value):
        super().__init__(MqttValueUpdateEvent, value=value)


class MqttValueChangeEventFilter(EventFilter):
    def __init__(self, *, value: Any = MISSING, old_value: Any = MISSING):
        args = {}
        if value is not MISSING:
            args['value'] = value
        if old_value is not MISSING:
            args['old_value'] = old_value
        super().__init__(MqttValueChangeEvent, **args)
