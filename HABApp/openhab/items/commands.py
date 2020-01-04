from .. import get_openhab_interface
from ..definitions import OnOffValue, UpDownValue


class OnOffCommand:

    def is_on(self) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_off(self) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()

    def on(self):
        """Command item on"""
        get_openhab_interface().send_command(self, OnOffValue.ON)

    def off(self):
        """Command item off"""
        get_openhab_interface().send_command(self, OnOffValue.OFF)


class PercentCommand:
    def percent(self, value: float):
        """Command to value (in percent)"""
        assert 0 <= value <= 100, value
        get_openhab_interface().send_command(self, str(value))


class UpDownCommand:
    def up(self):
        """Command up"""
        get_openhab_interface().send_command(self, UpDownValue.UP)

    def down(self):
        """Command down"""
        get_openhab_interface().send_command(self, UpDownValue.DOWN)

    def is_up(self) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_down(self) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()
