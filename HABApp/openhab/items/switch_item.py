from HABApp.core.items import Item
from .. import get_openhab_interface


class SwitchItem(Item):
    ON = 'ON'
    OFF = 'OFF'

    def set_value(self, new_state) -> bool:
        if new_state is not None and new_state != SwitchItem.ON and new_state != SwitchItem.OFF:
            raise ValueError(f'Invalid value for SwitchItem {self.name}: {new_state}')
        return super().set_value(new_state)

    def is_on(self) -> bool:
        """Test value against on-value"""
        return True if self.value == SwitchItem.ON else False

    def is_off(self) -> bool:
        """Test value against off-value"""
        return True if self.value == SwitchItem.OFF else False

    def on(self):
        """Command item on"""
        get_openhab_interface().send_command(self.name, SwitchItem.ON)

    def off(self):
        """Command item off"""
        get_openhab_interface().send_command(self.name, SwitchItem.OFF)

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
