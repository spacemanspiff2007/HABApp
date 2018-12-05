from .base_item import BaseItem

class ColorItem(BaseItem):

    def __init__(self):
        super().__init__()
        self.h = 0
        self.s = 0
        self.b = 0

    def update_state(self, _str):

        self.state = _str

        if _str is not None:
            h,s,b = _str.split(',')
            self.h = float(h)
            self.s = float(s)
            self.b = float(b)
