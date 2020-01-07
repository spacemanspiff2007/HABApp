from HABApp.core.items import Item
from ..definitions import QuantityValue


class StringItem(Item):
    """StringItem which accepts and converts the data types from OpenHAB"""


class LocationItem(Item):
    """LocationItem which accepts and converts the data types from OpenHAB"""

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)


class PlayerItem(Item):
    """PlayerItem which accepts and converts the data types from OpenHAB"""

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)
