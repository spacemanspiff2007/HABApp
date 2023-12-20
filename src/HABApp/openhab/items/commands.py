from HABApp.core.const.hints import HasNameAttr as _HasNameAttr
from HABApp.openhab.definitions import OnOffValue, UpDownValue
from HABApp.openhab.interface_sync import send_command


class OnOffCommand:

    def is_on(self: _HasNameAttr) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_off(self: _HasNameAttr) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()

    def on(self: _HasNameAttr):
        """Command item on"""
        send_command(self.name, OnOffValue.ON)

    def off(self: _HasNameAttr):
        """Command item off"""
        send_command(self.name, OnOffValue.OFF)


class PercentCommand:
    def percent(self: _HasNameAttr, value: float):
        """Command to value (in percent)"""
        assert 0 <= value <= 100, value
        send_command(self.name, str(value))


class UpDownCommand:
    def up(self: _HasNameAttr):
        """Command up"""
        send_command(self.name, UpDownValue.UP)

    def down(self: _HasNameAttr):
        """Command down"""
        send_command(self.name, UpDownValue.DOWN)

    def is_up(self: _HasNameAttr) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_down(self: _HasNameAttr) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()
