from .base_item import BaseItem

class ContactItem(BaseItem):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    def update_state(self, _str):
        if _str is not None and _str != ContactItem.OPEN and _str != ContactItem.CLOSED:
            raise ValueError(f'Invalid value for ContactItem: {_str}')
        self.state = _str

    def is_open(self):
        return True if self.state == ContactItem.OPEN else False

    def is_closed(self):
        return True if self.state == ContactItem.CLOSED else False