from .base_item import BaseItem

class StringItem(BaseItem):

    def update_state(self, _str):
        self.state = str(_str) if _str is not None else None

    def __str__(self):
        return self.state
