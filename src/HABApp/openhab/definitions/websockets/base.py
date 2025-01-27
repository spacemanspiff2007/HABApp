from pydantic import BaseModel as _BaseModel
from pydantic import ConfigDict, Field

from HABApp.openhab.events import OpenhabEvent


class BaseModel(_BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, populate_by_name=True)


class BaseEvent(BaseModel):
    topic: str

    source: str | None = None
    event_id: str | None = Field(None, alias='eventId')

    def to_event(self) -> OpenhabEvent:
        raise NotImplementedError()
