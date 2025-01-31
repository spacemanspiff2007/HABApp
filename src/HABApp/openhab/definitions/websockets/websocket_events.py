from typing import Annotated, Literal

from pydantic import Field, Json

from HABApp.core.const.const import StrEnum

from .base import SERIALIZE_TO_JSON_STR, BaseEvent, BaseOutEvent
from .item_value_types import ItemValueBase


class WebsocketTopicEnum(StrEnum):
    REQUEST_FAILED = 'openhab/websocket/response/failed'
    REQUEST_SUCCESS = 'openhab/websocket/response/success'
    HEARTBEAT = 'openhab/websocket/heartbeat'
    TYPE_FILTER = 'openhab/websocket/filter/type'


class WebsocketBaseEvent(BaseEvent):
    type: Literal['WebSocketEvent']


class WebsocketRequestFailedEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.REQUEST_FAILED]
    payload: str


class WebsocketRequestSuccessEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.REQUEST_SUCCESS]
    payload: Literal['']


class WebsocketHeartbeatEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.HEARTBEAT]
    payload: Literal['PONG', 'PING']


class WebsocketTypeFilterEvent(WebsocketBaseEvent):
    topic: Literal[WebsocketTopicEnum.TYPE_FILTER]
    payload: Json[list[str]]


WebsocketEventType = Annotated[
    WebsocketRequestFailedEvent |
    WebsocketRequestSuccessEvent |
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


class ItemStateSendEvent(BaseOutEvent):
    type: Literal['ItemStateEvent'] = 'ItemStateEvent'
    topic: str
    payload: Annotated[ItemValueBase, SERIALIZE_TO_JSON_STR]


class ItemCommandSendEvent(BaseOutEvent):
    type: Literal['ItemCommandEvent'] = 'ItemCommandEvent'
    topic: str
    payload: Annotated[ItemValueBase, SERIALIZE_TO_JSON_STR]

