from HABApp.core.items import Item
from ..definitions import QuantityValue


class NumberItem(Item):

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, QuantityValue):
            return super().set_value(new_value.value)

        return super().set_value(new_value)
