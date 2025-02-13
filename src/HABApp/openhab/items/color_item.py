from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from HABApp.core.errors import InvalidItemValueError, ItemValueIsNoneError
from HABApp.core.types import HSB, RGB
from HABApp.openhab.definitions.websockets.item_value_types import (
    HSBTypeModel,
)
from HABApp.openhab.items.base_item import MetaData, OpenhabItem, OutgoingCommandEvent, OutgoingStateEvent
from HABApp.openhab.items.commands import OnOffCommand, PercentCommand


if TYPE_CHECKING:
    Mapping = Mapping       # noqa: PLW0127
    MetaData = MetaData     # noqa: PLW0127


# https://github.com/openhab/openhab-core/blob/main/bundles/org.openhab.core/src/main/java/org/openhab/core/library/items/ColorItem.java
class ColorItem(OpenhabItem, OnOffCommand, PercentCommand):
    """ColorItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar HSB value: |oh_item_desc_value|

    :ivar str | None label: |oh_item_desc_label|
    :ivar frozenset[str] tags: |oh_item_desc_tags|
    :ivar frozenset[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    _update_to_oh: Final = OutgoingStateEvent('ColorItem', HSBTypeModel, 'Percent', 'OnOff', 'UnDef')
    _command_to_oh: Final = OutgoingCommandEvent(
        'ColorItem', HSBTypeModel, 'Percent', 'OnOff', 'IncreaseDecrease', 'Refresh')
    _state_from_oh_str = staticmethod(HSBTypeModel.get_value_from_state)

    @property
    def hsb(self) -> HSB:
        """HSB value"""
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v

    @property
    def hue(self) -> float:
        """Hue part of the value"""
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.hue

    @property
    def saturation(self) -> float:
        """Saturation part of the value"""
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.saturation

    @property
    def brightness(self) -> float:
        """Brightness part of the value"""
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.brightness

    @override
    def set_value(self, new_value: RGB | HSB | tuple[float, float, float]) -> bool:
        """Set a new color value without creating events on the event bus

        :param new_value: new value of the item
        :return: True if state has changed
        """

        if isinstance(new_value, HSB):
            hsb = new_value
        elif isinstance(new_value, RGB):
            hsb = new_value.to_hsb()
        elif isinstance(new_value, tuple):
            # map tuples to variables e.g. when calling post_value
            # when processing events instead of three values we get the tuple
            hue, saturation, brightness = new_value
            hsb = HSB(hue, saturation, brightness)
        elif new_value is None:
            hsb = None
        else:
            raise InvalidItemValueError.from_item(self, new_value)

        return super().set_value(new_value=hsb)

    def get_rgb(self) -> RGB:
        """Return a rgb equivalent of the color

        :return: rgb tuple
        """
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.to_rgb()

    def is_on(self) -> bool:
        """Return true if item is on"""
        if (value := self.value) is None:
            return False
        return value.brightness > 0

    def is_off(self) -> bool:
        """Return true if item is off"""
        if (value := self.value) is None:
            return False
        return value.brightness <= 0

    def __repr__(self) -> str:
        if self.value is None:
            return '<Color None>'
        return f'<Color hue: {self.hue}°, saturation: {self.saturation}%, brightness: {self.brightness}%>'
