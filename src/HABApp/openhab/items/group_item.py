from HABApp.core.events import ComplexEventValue
from HABApp.openhab.items.base_item import OpenhabItem


class GroupItem(OpenhabItem):
    """GroupItem which accepts and converts the data types from OpenHAB"""

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, ComplexEventValue):
            new_value = new_value.value
        return super().set_value(new_value)
