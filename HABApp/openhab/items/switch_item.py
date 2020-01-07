from HABApp.openhab.items.base_item import OpenhabItem
from HABApp.openhab.definitions.commands import OnOffCommand
from ..definitions import OnOffValue


class SwitchItem(OpenhabItem, OnOffCommand):

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OnOffValue):
            new_value = new_value.value

        if new_value is not None and new_value != OnOffValue.ON and new_value != OnOffValue.OFF:
            raise ValueError(f'Invalid value for SwitchItem {self.name}: {new_value}')
        return super().set_value(new_value)

    def is_on(self) -> bool:
        """Test value against on-value"""
        return True if self.value == OnOffValue.ON else False

    def is_off(self) -> bool:
        """Test value against off-value"""
        return True if self.value == OnOffValue.OFF else False

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, SwitchItem):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        elif isinstance(other, int):
            if other and self.is_on():
                return True
            if not other and self.is_off():
                return True
            return False

        return NotImplemented

    def __bool__(self):
        return self.is_on()
