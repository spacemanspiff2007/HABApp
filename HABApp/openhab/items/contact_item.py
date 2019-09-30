from HABApp.core.items import Item


class ContactItem(Item):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    def set_value(self, new_value) -> bool:
        if new_value is not None and new_value != ContactItem.OPEN and new_value != ContactItem.CLOSED:
            raise ValueError(f'Invalid value for ContactItem: {new_value}')
        return super().set_value(new_value)

    def is_open(self) -> bool:
        """Test value against open-value"""
        return True if self.value == ContactItem.OPEN else False

    def is_closed(self) -> bool:
        """Test value against closed-value"""
        return True if self.value == ContactItem.CLOSED else False

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
