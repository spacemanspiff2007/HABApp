import typing
import datetime

from HABApp.core.const import MISSING
from HABApp.core.items.base_valueitem import BaseValueItem
from HABApp.openhab.interface import post_update, send_command, get_persistence_data


class OpenhabItem(BaseValueItem):
    """Base class for items which exists in OpenHAB.
    """

    def oh_send_command(self, value: typing.Any = MISSING):
        """Send a command to the openHAB item

        :param value: (optional) value to be sent. If not specified the item value will be used.
        """
        send_command(self.name, self.value if value is MISSING else value)

    def oh_post_update(self, value: typing.Any = MISSING):
        """Post an update to the openHAB item

        :param value: (optional) value to be posted. If not specified the item value will be used.
        """
        post_update(self.name, self.value if value is MISSING else value)

    def get_persistence_data(self, persistence: typing.Optional[str] = None,
                             start_time: typing.Optional[datetime.datetime] = None,
                             end_time: typing.Optional[datetime.datetime] = None):
        """Query historical data from the OpenHAB persistence service

        :param persistence: name of the persistence service (e.g. ``rrd4j``, ``mapdb``). If not set default will be used
        :param start_time: return only items which are newer than this
        :param end_time: return only items which are older than this
        """

        return get_persistence_data(
            self.name, persistence, start_time, end_time
        )
