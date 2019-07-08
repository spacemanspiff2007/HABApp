from HABApp.core.items import Item
from .. import get_openhab_interface


class RollershutterItem(Item):

    def set_state(self, new_state):
        if new_state == 'UP':
            new_state = 0.0
        if new_state == 'DOWN':
            new_state = 100.0
        assert isinstance(new_state, (int, float)) or new_state is None, new_state
        super().set_state(new_state)

    def up(self):
        """Move shutter up"""
        get_openhab_interface().send_command(self.name, 'UP')

    def down(self):
        """Move shutter down"""
        get_openhab_interface().send_command(self.name, 'DOWN')

    def percent(self, value: float):
        """Command shutter to value (in percent)"""
        assert 0 <= value <= 100
        get_openhab_interface().send_command(self.name, str(value))

    def __str__(self):
        return self.state
