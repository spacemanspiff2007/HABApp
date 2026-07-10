
from aiomqtt.types import PayloadType

from HABApp.mqtt.connection.messages import MessagesHandler


class MqttLoopbackQueue:
    def __init__(self, handler: MessagesHandler) -> None:
        self.msg_handler: MessagesHandler = handler

    def put_nowait(self, obj: tuple[str, PayloadType, int, bool]) -> None:

        topic, payload, qos, retain = obj
        self.msg_handler.msg_to_event(topic, payload, retain=retain)
        return None
