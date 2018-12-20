from .base_item import BaseItem


class SwitchItem(BaseItem):
    ON = 'ON'
    OFF = 'OFF'

    def update_state(self, _str):
        if _str is not None and _str != SwitchItem.ON and _str != SwitchItem.OFF:
            raise ValueError(f'Invalid value for SwitchItem: {_str}')
        self.state = _str

    def is_on(self):
        return True if self.state == SwitchItem.ON else False

    def is_off(self):
        return True if self.state == SwitchItem.ON else False

    def __str__(self):
        return self.state
