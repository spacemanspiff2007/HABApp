from HABApp.openhab.items.base_item import OpenhabItem
from ..definitions import OpenClosedValue


class ContactItem(OpenhabItem):

    def set_value(self, new_value) -> bool:

        if isinstance(new_value, OpenClosedValue):
            new_value = new_value.value

        if new_value is not None and new_value != OpenClosedValue.OPEN and new_value != OpenClosedValue.CLOSED:
            raise ValueError(f'Invalid value for ContactItem: {new_value}')
        return super().set_value(new_value)

    def is_open(self) -> bool:
        """Test value against open-value"""
        return self.value == OpenClosedValue.OPEN

    def is_closed(self) -> bool:
        """Test value against closed-value"""
        return self.value == OpenClosedValue.CLOSED

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, ContactItem):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        elif isinstance(other, int):
            if other and self.is_open():
                return True
            if not other and self.is_closed():
                return True
            return False

        return NotImplemented
