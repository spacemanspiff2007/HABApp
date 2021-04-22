from HABApp.openhab.items.base_item import OpenhabItem
from ..definitions import QuantityValue


class StringItem(OpenhabItem):
    """StringItem which accepts and converts the data types from OpenHAB"""


class LocationItem(OpenhabItem):
    """LocationItem which accepts and converts the data types from OpenHAB"""

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)


class PlayerItem(OpenhabItem):
    """PlayerItem which accepts and converts the data types from OpenHAB"""

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)
