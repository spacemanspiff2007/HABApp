import typing

from HABApp.core.const import MISSING
from HABApp.core.items.base_valueitem import BaseValueItem
from HABApp.openhab import get_openhab_interface


class OpenhabItem(BaseValueItem):
    """Base class for items which exists in OpenHAB.
    """

    def oh_send_command(self, value: typing.Any = MISSING):
        """Send a command to the openHAB item

        :param value: (optional) value to be sent. If not specified the item value will be used.
        """
        get_openhab_interface().send_command(self.name, self.value if value is MISSING else value)

    def oh_post_update(self, value: typing.Any = MISSING):
        """Post an update to the openHAB item

        :param value: (optional) value to be posted. If not specified the item value will be used.
        """
        get_openhab_interface().post_update(self.name, self.value if value is MISSING else value)
