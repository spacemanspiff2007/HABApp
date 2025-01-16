from typing import Final

from HABApp.core.const.hints import HasNameAttr as _HasNameAttr
from HABApp.openhab.definitions import OnOffType, UpDownType
from HABApp.openhab.interface_sync import send_command


ON: Final = OnOffType.ON
OFF: Final = OnOffType.OFF
UP: Final = UpDownType.UP
DOWN: Final = UpDownType.DOWN


class OnOffCommand:

    def is_on(self: _HasNameAttr) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_off(self: _HasNameAttr) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()

    def on(self: _HasNameAttr) -> None:
        """Command item on"""
        send_command(self.name, ON)

    def off(self: _HasNameAttr) -> None:
        """Command item off"""
        send_command(self.name, OFF)


class PercentCommand:
    def percent(self: _HasNameAttr, value: float) -> None:
        """Command to value (in percent)"""
        send_command(self.name, self._command_to_oh.to_oh_str(value))


class UpDownCommand:

    def up(self: _HasNameAttr) -> None:
        """Command up"""
        send_command(self.name, UP)

    def down(self: _HasNameAttr) -> None:
        """Command down"""
        send_command(self.name, DOWN)

    def is_up(self: _HasNameAttr) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_down(self: _HasNameAttr) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()
