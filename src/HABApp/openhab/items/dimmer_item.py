from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.items.commands import OnOffCommand, PercentCommand
from ..definitions import OnOffValue, PercentValue


class DimmerItem(OpenhabItem, OnOffCommand, PercentCommand):

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = 100 if new_value.on else 0
        elif isinstance(new_value, PercentValue):
            new_value = new_value.value

        # Percent is 0 ... 100
        if isinstance(new_value, (int, float)):
            assert 0 <= new_value <= 100, new_value
        else:
            assert new_value is None, new_value

        return super().set_value(new_value)

    def __str__(self):
        return self.value

    def is_on(self) -> bool:
        """Test value against on-value"""
        return bool(self.value)

    def is_off(self) -> bool:
        """Test value against off-value"""
        return not bool(self.value)
