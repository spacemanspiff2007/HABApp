from HABApp.core.items import Item
from .. import get_openhab_interface


class DimmerItem(Item):

    def set_state(self, new_state):
        if new_state == 'ON':
            new_state = 100
        if new_state == 'OFF':
            new_state = 0

        assert isinstance(new_state, (int, float)) or new_state is None, new_state
        super().set_state(new_state)

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
        return self.state
