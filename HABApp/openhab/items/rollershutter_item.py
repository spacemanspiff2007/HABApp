from HABApp.core.items import Item
from .commands import UpDownCommand, PercentCommand
from ..definitions import UpDownValue, PercentValue


class RollershutterItem(Item, UpDownCommand, PercentCommand):

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, UpDownValue):
            new_value = 0 if new_value.up else 100
        elif isinstance(new_value, PercentValue):
            new_value = new_value.value

        assert isinstance(new_value, (int, float)) or new_value is None, new_value
        return super().set_value(new_value)

    def __str__(self):
        return self.value
