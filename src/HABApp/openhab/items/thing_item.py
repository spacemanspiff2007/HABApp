from typing import Any, Mapping

from immutables import Map
from pendulum import UTC
from pendulum import now as pd_now

from HABApp.core.items import BaseItem
from HABApp.openhab.definitions import ThingStatusEnum, ThingStatusDetailEnum
from HABApp.openhab.definitions.things import THING_STATUS_DEFAULT, THING_STATUS_DETAIL_DEFAULT
from HABApp.openhab.events import ThingConfigStatusInfoEvent, ThingStatusInfoEvent, ThingUpdatedEvent
from HABApp.openhab.interface_sync import set_thing_enabled


class Thing(BaseItem):
    """Base class for Things

    :ivar ThingStatusEnum status: Status of the thing (e.g. OFFLINE, ONLINE, ...)
    :ivar ThingStatusDetailEnum status_detail: Additional detail for the status
    :ivar str status_description: Additional description for the status
    :ivar str label: Thing label
    :ivar str location: Thing location
    :ivar Mapping[str, Any] configuration: Thing configuration
    :ivar Mapping[str, Any] properties: Thing properties
    """
    def __init__(self, name: str):
        super().__init__(name)

        self.status: ThingStatusEnum = THING_STATUS_DEFAULT
        self.status_detail: ThingStatusDetailEnum = THING_STATUS_DETAIL_DEFAULT
        self.status_description: str = ''

        self.label: str = ''
        self.location: str = ''

        self.configuration: Mapping[str, Any] = Map()
        self.properties: Mapping[str, Any] = Map()

    @property
    def is_enabled(self) -> bool:
        # https://github.com/openhab/openhab-core/issues/3055
        return self.status_detail != 'DISABLED'

    def __update_timestamps(self, changed: bool):
        _now = pd_now(UTC)
        self._last_update.set(_now)
        if changed:
            self._last_change.set(_now)
        return None

    def process_event(self, event):

        if isinstance(event, ThingStatusInfoEvent):
            old_status = self.status
            old_detail = self.status_detail
            old_description = self.status_description

            self.status = new_status = event.status
            self.status_detail = new_detail = event.detail
            self.status_description = new_description = event.description

            self.__update_timestamps(
                old_status != new_status or old_detail != new_detail or old_description != new_description
            )
        elif isinstance(event, ThingUpdatedEvent):
            old_label = self.label
            old_configuration = self.configuration
            old_properties = self.properties
            old_location = self.location

            self.label = new_label = event.label
            self.location = new_location = event.location
            self.configuration = new_configuration = Map(event.configuration)
            self.properties = new_properties = Map(event.properties)

            self.__update_timestamps(
                old_label != new_label or old_location != new_location or   # noqa: W504
                old_configuration != new_configuration or old_properties != new_properties
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
