from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field, PlainSerializer
from pydantic_core import to_json

from HABApp.openhab.events import OpenhabEvent


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, validate_default=True, validate_assignment=True)


class BaseEvent(BaseModel):
    topic: str

    source: str | None = None
    event_id: str | None = Field(None, alias='eventId')

    def to_event(self) -> OpenhabEvent:
        raise NotImplementedError()


SERIALIZE_TO_JSON_STR = PlainSerializer(lambda x: to_json(x).decode())


MSG_CTR: int = 1


def msg_id() -> str:
    global MSG_CTR

    value = MSG_CTR

    MSG_CTR += 1
    if MSG_CTR >= 1_000_000:  # noqa: PLR2004
        MSG_CTR = 1

    return str(value)


class BaseOutEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    topic: str

    source: str = 'HABApp'
    event_id: str  = Field(default_factory=msg_id, alias='eventId')
