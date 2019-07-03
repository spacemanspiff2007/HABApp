import colorsys
import typing

from . import Item

HUE_FACTOR = 360
PERCENT_FACTOR = 100


class ColorItem(Item):
    def __init__(self, name: str, h=0.0, s=0.0, v=0.0):
        super().__init__(name=name, state=(h, s, v))

        self.hue: float = min(max(0.0, h), HUE_FACTOR)
        self.saturation: float = min(max(0.0, s), PERCENT_FACTOR)
        self.value: float = min(max(0.0, v), PERCENT_FACTOR)

    def set_state(self, h=0.0, s=0.0, v=0.0):
        self.hue = min(max(0.0, h), HUE_FACTOR)
        self.saturation = min(max(0.0, s), PERCENT_FACTOR)
        self.value = min(max(0.0, v), PERCENT_FACTOR)

        super().set_state(new_state=(h, s, v))

    def get_rgb(self, max_rgb_value=255) -> typing.Tuple[int, int, int]:
        r, g, b = colorsys.hsv_to_rgb(
            self.hue / HUE_FACTOR,
            self.saturation / PERCENT_FACTOR,
            self.value / PERCENT_FACTOR
        )
        return int(r * max_rgb_value), int(g * max_rgb_value), int(b * max_rgb_value)

    def set_rgb(self, r, g, b, max_rgb_value=255):
        h, s, v = colorsys.rgb_to_hsv(r / max_rgb_value, g / max_rgb_value, b / max_rgb_value)
        self.hue = h * HUE_FACTOR
        self.saturation = s * PERCENT_FACTOR
        self.value = v * PERCENT_FACTOR
        return self

    def __repr__(self):
        return f'<Color Hue: {self.hue}°, Saturation: {self.saturation}%, Value: {self.value}%>'
