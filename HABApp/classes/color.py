import colorsys
import typing


class Color:
    RGB_FACTOR = 255
    HUE_FACTOR = 360
    PERCENT_FACTOR = 100

    def __init__(self, h=0.0, s=0.0, v=0.0):
        self.hue = min(max(0, h), Color.HUE_FACTOR)
        self.saturation = min(max(0, s), Color.PERCENT_FACTOR)
        self.value = min(max(0, v), Color.PERCENT_FACTOR)

    def get_rgb(self) -> typing.Tuple[int, int, int]:
        r, g, b = colorsys.hsv_to_rgb(
            self.hue / Color.HUE_FACTOR,
            self.saturation / Color.PERCENT_FACTOR,
            self.value / Color.PERCENT_FACTOR
        )
        return int(r * Color.RGB_FACTOR), int(g * Color.RGB_FACTOR), int(b * Color.RGB_FACTOR)

    def set_rgb(self, r, g, b):
        h, s, v = colorsys.rgb_to_hsv(r / Color.RGB_FACTOR, g / Color.RGB_FACTOR, b / Color.RGB_FACTOR)
        self.hue = h * Color.HUE_FACTOR
        self.saturation = s * Color.PERCENT_FACTOR
        self.value = v * Color.PERCENT_FACTOR
        return self

    def __repr__(self):
        return f'<Color Hue: {self.hue}°, Saturation: {self.saturation}%, Value: {self.value}%>'
