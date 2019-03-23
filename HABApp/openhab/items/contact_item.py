from HABApp.core.items import Item


class ContactItem(Item):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    @classmethod
    def from_str(self, name, value):
        item = ContactItem(name=name)
        item.set_state(value)
        return item

    def set_state(self, new_state):
        if new_state is not None and new_state != ContactItem.OPEN and new_state != ContactItem.CLOSED:
            raise ValueError(f'Invalid value for ContactItem: {new_state}')
        super().set_state(new_state)

    def is_open(self):
        return True if self.state == ContactItem.OPEN else False

    def is_closed(self):
        return True if self.state == ContactItem.CLOSED else False

    def __str__(self):
        return self.state

    def __eq__(self, other):
        if isinstance(other, ContactItem):
            return self.state == other.state
        elif isinstance(other, str):
            return self.state == other
        elif isinstance(other, int):
            if other and self.is_open():
                return True
            if not other and self.is_closed():
                return True
            return False

        return NotImplemented

    def __ne__(self, other):
        res = self.__eq__(other)
        if res is NotImplemented:
            return res
        return not res
