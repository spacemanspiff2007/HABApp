import HABApp


class MqttValueUpdateEvent(HABApp.core.events.ValueUpdateEvent):
    __slots__ = ()


class MqttValueChangeEvent(HABApp.core.events.ValueChangeEvent):
    __slots__ = ()
