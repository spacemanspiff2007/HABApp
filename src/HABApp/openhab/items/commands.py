from __future__ import annotations

from typing import TYPE_CHECKING

from HABApp.core.errors import InvalidItemValueError
from HABApp.openhab.definitions.websockets import ItemCommandSendEvent
from HABApp.openhab.definitions.websockets.item_value_types import OnOffTypeModel, PercentTypeModel, UpDownTypeModel


if TYPE_CHECKING:
    from HABApp.openhab.items import OpenhabItem


class OnOffCommand:

    def is_on(self: OpenhabItem) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_off(self: OpenhabItem) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()

    def on(self: OpenhabItem) -> None:
        """Command item on"""
        self._oh._send_websocket_event(
            ItemCommandSendEvent.create(self.name, OnOffTypeModel(type='OnOff', value='ON'))
        )

    def off(self: OpenhabItem) -> None:
        """Command item off"""
        self._oh._send_websocket_event(
            ItemCommandSendEvent.create(self.name, OnOffTypeModel(type='OnOff', value='OFF'))
        )


class PercentCommand:
    def percent(self: OpenhabItem, value: float) -> None:
        """Command to value (in percent)"""
        if not 0 <= value <= 100:
            raise InvalidItemValueError.from_item(self, value)

        self._oh._send_websocket_event(
            ItemCommandSendEvent.create(self.name, PercentTypeModel(type='Percent', value=str(value)))
        )


class UpDownCommand:

    def up(self: OpenhabItem) -> None:
        """Command up"""
        self._oh._send_websocket_event(
            ItemCommandSendEvent.create(self.name, UpDownTypeModel(type='UpDown', value='UP'))
        )

    def down(self: OpenhabItem) -> None:
        """Command down"""
        self._oh._send_websocket_event(
            ItemCommandSendEvent.create(self.name, UpDownTypeModel(type='UpDown', value='DOWN'))
        )

    def is_up(self: OpenhabItem) -> bool:
        """Test value against on-value"""
        raise NotImplementedError()

    def is_down(self: OpenhabItem) -> bool:
        """Test value against off-value"""
        raise NotImplementedError()
