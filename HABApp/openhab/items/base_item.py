import typing

from HABApp.core.items.base_valueitem import BaseValueItem
from HABApp.openhab import get_openhab_interface


class OpenhabItem(BaseValueItem):
    """Base class for items which exists in OpenHAB.
    """

    def send_command(self, value: typing.Any):
        """Send a command to the openHAB item

        :param value:
        """
        get_openhab_interface().send_command(self.name, value)
