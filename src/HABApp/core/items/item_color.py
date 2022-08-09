import typing
from typing import Optional

from HABApp.core.errors import ItemNotFoundException
from HABApp.core.internals import uses_item_registry
from HABApp.core.items import BaseValueItem
from HABApp.core.lib import hsb_to_rgb, rgb_to_hsb

HUE_FACTOR = 360
PERCENT_FACTOR = 100

item_registry = uses_item_registry()


class ColorItem(BaseValueItem):
    """Item for dealing with color related values"""

    def __init__(self, name: str, hue=0.0, saturation=0.0, brightness=0.0):
        super().__init__(name=name, initial_value=(hue, saturation, brightness))

        self.hue: float = min(max(0.0, hue), HUE_FACTOR)
        self.saturation: float = min(max(0.0, saturation), PERCENT_FACTOR)
        self.brightness: float = min(max(0.0, brightness), PERCENT_FACTOR)

    def set_value(self, hue=0.0, saturation=0.0, brightness=0.0):
        """Set the color value

        :param hue: hue (in °)
        :param saturation: saturation (in %)
        :param brightness: brightness (in %)
        """

        # map tuples to variables
        # when processing events instead of three values we get the tuple
        if isinstance(hue, tuple):
            hue, saturation, brightness = hue

        # with None we use the already set value
        self.hue = min(max(0.0, hue), HUE_FACTOR) if hue is not None else self.hue
        self.saturation = min(max(0.0, saturation), PERCENT_FACTOR) if saturation is not None else self.saturation
        self.brightness = min(max(0.0, brightness), PERCENT_FACTOR) if brightness is not None else self.brightness

        return super().set_value(new_value=(self.hue, self.saturation, self.brightness))

    def post_value(self, hue=0.0, saturation=0.0, brightness=0.0):
        """Set a new value and post appropriate events on the HABApp event bus
        (``ValueUpdateEvent``, ``ValueChangeEvent``)

        :param hue: hue (in °)
        :param saturation: saturation (in %)
        :param brightness: brightness (in %)
        """
        super().post_value(
            # encapsulate in tuple !
            (hue if hue is not None else self.hue,
             saturation if saturation is not None else self.saturation,
             brightness if brightness is not None else self.brightness)
        )

    def get_rgb(self, max_rgb_value=255) -> typing.Tuple[int, int, int]:
        """Return a rgb equivalent of the color

        :param max_rgb_value: the max value for rgb, typically 255 (default) or 65.536
        :return: rgb tuple
        """
        return hsb_to_rgb(self.hue, self.saturation, self.brightness, max_rgb_value=max_rgb_value)

    def set_rgb(self, r, g, b, max_rgb_value=255, ndigits: Optional[int] = 2) -> 'ColorItem':
        """Set a rgb value

        :param r: red value
        :param g: green value
        :param b: blue value
        :param max_rgb_value: the max value for rgb, typically 255 (default) or 65.536
        :param ndigits: Round the hsb values to the specified digits, None to disable rounding
        :return: self
        """
        h, s, b = rgb_to_hsb(r, g, b, max_rgb_value=max_rgb_value, ndigits=ndigits)
        self.set_value(h, s, b)
        return self

    def post_rgb(self, r, g, b, max_rgb_value=255) -> 'ColorItem':
        """Set a new rgb value and post appropriate events on the HABApp event bus
        (``ValueUpdateEvent``, ``ValueChangeEvent``)

        :param r: red value
        :param g: green value
        :param b: blue value
        :param max_rgb_value: the max value for rgb, typically 255 (default) or 65.536
        :return: self
        """
        self.set_rgb(r, g, b, max_rgb_value=max_rgb_value)
        self.post_value(self.hue, self.saturation, self.brightness)
        return self

    def is_on(self) -> bool:
        """Return true if item is on"""
        return self.brightness > 0

    def is_off(self) -> bool:
        """Return true if item is off"""
        return self.brightness <= 0

    def __repr__(self):
        return f'<Color hue: {self.hue}°, saturation: {self.saturation}%, brightness: {self.brightness}%>'

    @classmethod
    def get_create_item(cls, name: str, hue=0.0, saturation=0.0, brightness=0.0):
        """Creates a new item in HABApp and returns it or returns the already existing one with the given name

        :param name: item name
        :param initial_value: state the item will have if it gets created
        :return: item
        """
        assert isinstance(name, str), type(name)

        try:
            item = item_registry.get_item(name)
        except ItemNotFoundException:
            item = item_registry.add_item(cls(name, hue=hue, saturation=saturation, brightness=brightness))

        assert isinstance(item, cls), f'{cls} != {type(item)}'
        return item
