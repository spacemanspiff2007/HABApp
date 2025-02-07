from HABApp.core.const.hints import HasNameAttr as _HasNameAttr
from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.connection.plugins import send_websocket_event
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import OnOffTypeModel, PercentTypeModel, UpDownTypeModel


class OnOffCommand:

    def is_on(self: _HasNameAttr) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_off(self: _HasNameAttr) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()

    def on(self: _HasNameAttr) -> None:
        """Command item on"""
        send_websocket_event(
            ItemCommandSendEvent.create(self.name, OnOffTypeModel(type='OnOff', value='ON'))
        )

    def off(self: _HasNameAttr) -> None:
        """Command item off"""
        send_websocket_event(
            ItemCommandSendEvent.create(self.name, OnOffTypeModel(type='OnOff', value='OFF'))
        )


class PercentCommand:
    def percent(self: _HasNameAttr, value: float) -> None:
        """Command to value (in percent)"""
        if not 0 <= value <= 100:
            raise InvalidItemValueError.from_item(self, value)

        send_websocket_event(
            ItemCommandSendEvent.create(self.name, PercentTypeModel(type='Percent', value=str(value)))
        )


class UpDownCommand:

    def up(self: _HasNameAttr) -> None:
        """Command up"""
        send_websocket_event(
            ItemCommandSendEvent.create(self.name, UpDownTypeModel(type='UpDown', value='UP'))
        )

    def down(self: _HasNameAttr) -> None:
        """Command down"""
        send_websocket_event(
            ItemCommandSendEvent.create(self.name, UpDownTypeModel(type='UpDown', value='DOWN'))
        )

    def is_up(self: _HasNameAttr) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_down(self: _HasNameAttr) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()
