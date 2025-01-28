from typing import Annotated, Literal

from pydantic import Field, Json

from HABApp.core.const.const import StrEnum

from .base import SERIALIZE_TO_JSON_STR, BaseEvent, BaseOutEvent


class WebsocketTopicEnum(StrEnum):
    REQUEST_FAILED = 'openhab/websocket/response/failed'
    HEARTBEAT = 'openhab/websocket/heartbeat'
    TYPE_FILTER = 'openhab/websocket/filter/type'


class WebsocketBaseEvent(BaseEvent):
    type: Literal['WebSocketEvent']


class WebsocketRequestFailedEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.REQUEST_FAILED]
    payload: str


class WebsocketHeartbeatEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.HEARTBEAT]
    payload: Literal['PONG', 'PING']


class WebsocketTypeFilterEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.TYPE_FILTER]
    payload: Json[list[str]]


WebsocketEventType = Annotated[
    WebsocketRequestFailedEvent |
    WebsocketHeartbeatEvent |
    WebsocketTypeFilterEvent,
    Field(discriminator='topic')
]


# ----------------------------------------------------------------------------------------------------------------------
# Outgoing events
# ----------------------------------------------------------------------------------------------------------------------
class WebsocketSendTypeFilter(BaseOutEvent):
    type: Literal['WebSocketEvent'] = 'WebSocketEvent'
    topic: Literal[WebsocketTopicEnum.TYPE_FILTER] = WebsocketTopicEnum.TYPE_FILTER
    payload: Annotated[list[str], SERIALIZE_TO_JSON_STR]
