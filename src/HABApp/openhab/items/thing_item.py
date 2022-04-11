from typing import Optional

from pendulum import UTC
from pendulum import now as pd_now

from HABApp.core.items import BaseItem
from ..events import ThingStatusInfoEvent


class Thing(BaseItem):
    """Base class for Things

    :ivar str status: Status of the thing (e.g. OFFLINE, ONLINE, ...)
    :ivar str status_detail: Additional detail for the status
    """
    def __init__(self, name: str):
        super().__init__(name)

        self.status: str = ''
        self.status_detail: str = ''

    def __update_timestamps(self, changed: bool):
        _now = pd_now(UTC)
        self._last_update.set(_now)
        if changed:
            self._last_change.set(_now)
        return None

    def process_event(self, event):

        if isinstance(event, ThingStatusInfoEvent):
            old = self.status
            self.status = new = event.status
            self.status_detail = event.detail

            self.__update_timestamps(old == new)

        return None
