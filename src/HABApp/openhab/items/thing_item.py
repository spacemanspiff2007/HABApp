from typing import Any
from typing import Mapping

from immutables import Map
from pendulum import UTC
from pendulum import now as pd_now

from HABApp.core.items import BaseItem
from HABApp.openhab.events import ThingStatusInfoEvent, ThingUpdatedEvent, ThingConfigStatusInfoEvent
from HABApp.openhab.interface import set_thing_enabled


class Thing(BaseItem):
    """Base class for Things

    :ivar str status: Status of the thing (e.g. OFFLINE, ONLINE, ...)
    :ivar str status_detail: Additional detail for the status
    :ivar str label: Thing label
    :ivar Mapping[str, Any] configuration: Thing configuration
    :ivar Mapping[str, Any] properties: Thing properties
    """
    def __init__(self, name: str):
        super().__init__(name)

        self.status: str = ''
        self.status_detail: str = ''

        self.label: str = ''

        self.configuration: Mapping[str, Any] = Map()
        self.properties: Mapping[str, Any] = Map()

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

            self.__update_timestamps(old != new)
        elif isinstance(event, ThingUpdatedEvent):
            old_label         = self.label
            old_configuration = self.configuration
            old_properties    = self.properties

            self.label         = event.label
            self.configuration = Map(event.configuration)
            self.properties    = Map(event.properties)

            self.__update_timestamps(
                old_label != self.label or old_configuration != self.configuration or old_properties != self.properties
            )
        elif isinstance(event, ThingConfigStatusInfoEvent):
            pass

        return None

    def set_enabled(self, enable: bool = True):
        """Enable/disable the thing

        :param enable: True to enable, False to disable the thing
        :return:
        """
        return set_thing_enabled(self.name, enable)
