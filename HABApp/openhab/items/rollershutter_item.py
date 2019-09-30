from HABApp.core.items import Item
from .. import get_openhab_interface


class RollershutterItem(Item):

    def set_value(self, new_value) -> bool:
        if new_value == 'UP':
            new_value = 0.0
        if new_value == 'DOWN':
            new_value = 100.0
        assert isinstance(new_value, (int, float)) or new_value is None, new_value
        return super().set_value(new_value)

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
        return self.value
