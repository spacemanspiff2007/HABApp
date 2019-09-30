from HABApp.core.items import Item
from .. import get_openhab_interface


class DimmerItem(Item):

    def set_value(self, new_value) -> bool:
        if new_value == 'ON':
            new_value = 100
        if new_value == 'OFF':
            new_value = 0

        assert isinstance(new_value, (int, float)) or new_value is None, new_value
        return super().set_value(new_value)

    def on(self):
        """Switch on"""
        get_openhab_interface().send_command(self.name, 'ON')

    def off(self):
        """Switch off"""
        get_openhab_interface().send_command(self.name, 'OFF')

    def percent(self, value: float):
        """Command dimmer to value (in percent)"""
        assert 0 <= value <= 100
        get_openhab_interface().send_command(self.name, str(value))

    def __str__(self):
        return self.value
