from colorsys import hsv_to_rgb as _hsv_to_rgb
from colorsys import rgb_to_hsv as _rgb_to_hsv
from typing import Optional, Tuple, Union


def rgb_to_hsb(r: Union[int, float], g: Union[int, float], b: Union[int, float],
               max_rgb_value: int = 255, ndigits: Optional[int] = 2) -> Tuple[float, float, float]:
    """Convert from rgb to hsb/hsv

    :param r: red value
    :param g: green value
    :param b: blue value
    :param max_rgb_value: maximal possible rgb value (e.g. 255 for 8 bit or 65.535 for 16bit values)
    :param ndigits: Round the hsb values to the specified digits, None to disable rounding
    :return: Values for hue, saturation and brightness / value
    """
    h, s, v = _rgb_to_hsv(r / max_rgb_value, g / max_rgb_value, b / max_rgb_value)
    h *= 360
    s *= 100
    v *= 100

    if ndigits is not None:
        h = round(h, ndigits)
        s = round(s, ndigits)
        v = round(v, ndigits)

    return h, s, v


def hsb_to_rgb(h, s, b, max_rgb_value=255) -> Tuple[int, int, int]:
    """Convert from rgb to hsv/hsb

    :param h: hue
    :param s: saturation
    :param b: brightness / value
    :param max_rgb_value: maximal value for the returned rgb values (e.g. 255 for 8 bit or 65.535 16bit values)
    :return: Values for red, green and blue
    """
    r, g, b = _hsv_to_rgb(h / 360, s / 100, b / 100)
    return round(r * max_rgb_value), round(g * max_rgb_value), round(b * max_rgb_value)
