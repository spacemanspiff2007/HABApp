from HABApp.openhab.items.base_item import OpenhabItem


class StringItem(OpenhabItem):
    """StringItem which accepts and converts the data types from OpenHAB"""


class LocationItem(OpenhabItem):
    """LocationItem which accepts and converts the data types from OpenHAB"""


class PlayerItem(OpenhabItem):
    """PlayerItem which accepts and converts the data types from OpenHAB"""


class CallItem(OpenhabItem):
    """CallItem which accepts and converts the data types from OpenHAB"""

    def set_value(self, new_value) -> bool:
        if isinstance(new_value, str) and ',' in new_value:
            new_value = tuple(new_value.split(','))
        return super().set_value(new_value)
