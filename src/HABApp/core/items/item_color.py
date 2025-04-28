from typing_extensions import Self, override

from HABApp.core.errors import (
    InvalidItemValueError,
    ItemNameNotOfTypeStrError,
    ItemNotFoundException,
    ItemValueIsNoneError,
    WrongItemTypeError,
)
from HABApp.core.internals import uses_item_registry
from HABApp.core.items import BaseValueItem
from HABApp.core.types import HSB, RGB


item_registry = uses_item_registry()


class ColorItem(BaseValueItem):
    """Item for dealing with color related values"""

    value: HSB | None

    @property
    def hsb(self) -> HSB:
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v

    @property
    def hue(self) -> float:
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.hue

    @property
    def saturation(self) -> float:
        if (v := self.value) is None:
            raise ItemValueIsNoneError.from_item(self)
        return v.saturation

    @property
    def brightness(self) -> float:
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
            # Convert tuple to HSB
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
        if self.value is None:
            return False
        return self.value.brightness > 0

    def is_off(self) -> bool:
        """Return true if item is off"""
        if self.value is None:
            return False
        return self.value.brightness <= 0

    def __repr__(self) -> str:
        if self.value is None:
            return '<Color None>'
        return f'<Color hue: {self.hue}°, saturation: {self.saturation}%, brightness: {self.brightness}%>'

    @classmethod
    def get_create_item(cls, name: str,
                        initial_value: RGB | HSB | tuple[float, float, float] | None = None) -> Self:
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :param hue: hue (if initial_value is not used)
        :param saturation: saturation (if initial_value is not used)
        :param brightness: brightness (if initial_value is not used)
        :return: item
        """
        if not isinstance(name, str):
            raise ItemNameNotOfTypeStrError.from_value(name)

        try:
            item = item_registry.get_item(name)
        except ItemNotFoundException:
            item = item_registry.add_item(cls(name, initial_value))

        if not isinstance(item, cls):
            raise WrongItemTypeError.from_item(item, cls)
        return item
