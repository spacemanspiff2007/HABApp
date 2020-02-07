import colorsys
import typing

from .base_valueitem import BaseValueItem

HUE_FACTOR = 360
PERCENT_FACTOR = 100


class ColorItem(BaseValueItem):
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
        """Set a new value and post appropriate events on the HABApp event bus (``ValueUpdateEvent``, ``ValueChangeEvent``)

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
        r, g, b = colorsys.hsv_to_rgb(
            self.hue / HUE_FACTOR,
            self.saturation / PERCENT_FACTOR,
            self.brightness / PERCENT_FACTOR
        )
        return int(r * max_rgb_value), int(g * max_rgb_value), int(b * max_rgb_value)

    def set_rgb(self, r, g, b, max_rgb_value=255) -> 'ColorItem':
        """Set a rgb value

        :param r: red value
        :param g: green value
        :param b: blue value
        :param max_rgb_value: the max value for rgb, typically 255 (default) or 65.536
        :return: self
        """
        h, s, v = colorsys.rgb_to_hsv(r / max_rgb_value, g / max_rgb_value, b / max_rgb_value)
        self.hue = h * HUE_FACTOR
        self.saturation = s * PERCENT_FACTOR
        self.brightness = v * PERCENT_FACTOR
        self.set_value(self.hue, self.saturation, self.brightness)
        return self

    def post_rgb(self, r, g, b, max_rgb_value=255) -> 'ColorItem':
        """Set a new rgb value and post appropriate events on the HABApp event bus (``ValueUpdateEvent``, ``ValueChangeEvent``)

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
