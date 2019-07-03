from HABApp.core.items import NumericItem
from .. import get_openhab_interface


class RollershutterItem(NumericItem):

    def set_state(self, new_state):
        if new_state == 'UP':
            new_state = 0.0
        if new_state == 'DOWN':
            new_state = 100.0
        assert isinstance(new_state, (int, float)) or new_state is None, new_state
        super().set_state(new_state)

    def up(self):
        """Switch on"""
        get_openhab_interface().send_command(self.name, 'UP')

    def down(self):
        """Switch off"""
        get_openhab_interface().send_command(self.name, 'DOWN')

    def percent(self, value: float):
        """Set shutter to value (in percent)"""
        assert 0 <= value <= 100
        get_openhab_interface().send_command(self.name, str(value))

    def __str__(self):
        return self.state
