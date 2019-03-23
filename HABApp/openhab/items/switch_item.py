from HABApp.core.items import Item


class SwitchItem(Item):
    ON = 'ON'
    OFF = 'OFF'

    @classmethod
    def from_str(self, name, value):
        item = SwitchItem(name=name)
        item.set_state(value)
        return item

    def set_state(self, new_state):
        if new_state is not None and new_state != SwitchItem.ON and new_state != SwitchItem.OFF:
            raise ValueError(f'Invalid value for SwitchItem {self.name}: {new_state}')
        super().set_state(new_state)

    def is_on(self):
        return True if self.state == SwitchItem.ON else False

    def is_off(self):
        return True if self.state == SwitchItem.OFF else False

    def __str__(self):
        return self.state

    def __eq__(self, other):
        if isinstance(other, SwitchItem):
            return self.state == other.state
        elif isinstance(other, str):
            return self.state == other
        elif isinstance(other, int):
            if other and self.is_on():
                return True
            if not other and self.is_off():
                return True
            return False

        return NotImplemented

    def __ne__(self, other):
        res = self.__eq__(other)
        if res is NotImplemented:
            return res
        return not res
