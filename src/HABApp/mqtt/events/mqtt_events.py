import HABApp


class MqttValueUpdateEvent(HABApp.core.events.ValueUpdateEvent):
    # Copy the annotations, otherwise the code won't work from py3.10 on
    __annotations__ = HABApp.core.events.ValueUpdateEvent.__annotations__.copy()


class MqttValueChangeEvent(HABApp.core.events.ValueChangeEvent):
    # Copy the annotations, otherwise the code won't work from py3.10 on
    __annotations__ = HABApp.core.events.ValueChangeEvent.__annotations__.copy()
