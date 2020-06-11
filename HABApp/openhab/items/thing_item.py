from datetime import datetime

from pytz import utc

from HABApp.core.items.base_item import BaseItem
from ..events import ThingStatusInfoEvent


class Thing(BaseItem):
    """Base class for Things

    :ivar str status: Status of the thing (e.g. OFFLINE, ONLINE, ...)
    """
    def __init__(self, name: str):
        super().__init__(name)

        self.status: str = ''

    def __update_timestamps(self, changed: bool):
        _now = datetime.now(tz=utc)
        self._last_update.set(_now)
        if changed:
            self._last_change.set(_now)
        return None

    def process_event(self, event):

        if isinstance(event, ThingStatusInfoEvent):
            old = self.status
            self.status = event.status
            self.__update_timestamps(old == self.status)

        return None
