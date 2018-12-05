import datetime

from .base_item import BaseItem

class DateTimeItem(BaseItem):

    def update_state(self, _str):
        self.state = datetime.datetime.strptime(_str.replace('+', '000+'), '%Y-%m-%dT%H:%M:%S.%f%z') if _str is not None else None
