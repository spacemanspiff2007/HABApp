from HABApp.core.items import Item
from .. import get_openhab_interface


class RollershutterItem(Item):

    def set_state(self, new_state) -> bool:
        if new_state == 'UP':
            new_state = 0.0
        if new_state == 'DOWN':
            new_state = 100.0
        assert isinstance(new_state, (int, float)) or new_state is None, new_state
        return super().set_state(new_state)

    def up(self):
        """Move shutter up"""
        get_openhab_interface().send_command(self.name, 'UP')

    def down(self):
        """Move shutter down"""
        get_openhab_interface().send_command(self.name, 'DOWN')

    def percent(self, percent: float):
        """Command shutter to value (in percent)

        :param percent: target position in percent
        :return:
        """
        assert 0 <= percent <= 100
        get_openhab_interface().send_command(self.name, str(percent))

    def __str__(self):
        return self.state
