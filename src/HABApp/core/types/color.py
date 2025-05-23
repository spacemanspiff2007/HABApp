from __future__ import annotations

from colorsys import hsv_to_rgb as _hsv_to_rgb
from colorsys import rgb_to_hsv as _rgb_to_hsv
from typing import Final

from typing_extensions import Self


class ColorType:
    __slots__ = ()


class RGB(ColorType):
    __slots__ = ('_r', '_g', '_b')  # noqa: RUF023

    _RGB_MAX: int = 2 ** 8 - 1

    def __init__(self, r: int, g: int, b: int) -> None:
        max_value = self._RGB_MAX
        if not 0 <= r <= max_value or not 0 <= g <= max_value or not 0 <= b <= max_value:
            raise ValueError()

        self._r: int = r
        self._g: int = g
        self._b: int = b

    @property
    def red(self) -> int:
        """red value"""
        return self._r

    @property
    def r(self) -> int:
        """red value"""
        return self._r

    @property
    def green(self) -> int:
        """green value"""
        return self._g

    @property
    def g(self) -> int:
        """green value"""
        return self._g

    @property
    def blue(self) -> int:
        """blue value"""
        return self._b

    @property
    def b(self) -> int:
        """blue value"""
        return self._b

    def replace(self, r: int | None = None, g: int | None = None, b: int | None = None,
                red: int | None = None, green: int | None = None, blue: int | None = None) -> Self:
        """Create a new object with (optionally) replaced values.

        :param r: new red value
        :param red: new red value
        :param g: new green value
        :param green: new green value
        :param b: new blue value
        :param blue: new blue value
        """

        if r is not None:
            if red is not None:
                raise ValueError()
            red = r

        if g is not None:
            if green is not None:
                raise ValueError()
            green = g

        if b is not None:
            if blue is not None:
                raise ValueError()
            blue = b

        return self.__class__(
            red if red is not None else self._r,
            green if green is not None else self._g,
            blue if blue is not None else self._b,
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._r:d}, {self._g:d}, {self._b})'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._r == other._r and self._g == other._g and self._b == other._b
        if isinstance(other, HSB):
            return self == self.__class__.from_hsb(other)
        return NotImplemented

    def __getitem__(self, item: int | str) -> int:
        if isinstance(item, int):
            if item == 0:
                return self._r
            if item == 1:
                return self._g
            if item == 2:
                return self._b
            raise IndexError()

        if isinstance(item, str):
            if item in ('r', 'red'):
                return self._r
            if item in ('g', 'green'):
                return self._g
            if item in ('b', 'blue'):
                return self._b
            raise KeyError()

        raise TypeError()

    # ------------------------------------------------------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------------------------------------------------------
    def to_hsb(self) -> HSB:
        """Create a new HSB object from this object

        :return: New HSB object
        """
        max_value = self._RGB_MAX
        h, s, v = _rgb_to_hsv(self._r / max_value, self._g / max_value, self._b / max_value)
        return HSB(h * HUE_FACTOR, s * PERCENT_FACTOR, v * PERCENT_FACTOR)

    @classmethod
    def from_hsb(cls, obj: HSB | tuple[float, float, float]) -> Self:
        """Return new Object from a HSB object for a hsb tuple

        :param obj: HSB object or tuple with HSB values
        :return: new RGB object
        """
        max_value = cls._RGB_MAX
        h, s, b = (obj._hue, obj._saturation, obj._brightness) if isinstance(obj, HSB) else obj
        r, g, b = _hsv_to_rgb(h / HUE_FACTOR, s / PERCENT_FACTOR, b / PERCENT_FACTOR)
        return cls(round(r * max_value), round(g * max_value), round(b * max_value))


class RGB16(RGB):
    _RGB_MAX: int = 2 ** 16 - 1


class RGB24(RGB):
    _RGB_MAX: int = 2 ** 32 - 1


class RGB32(RGB):
    _RGB_MAX: int = 2 ** 32 - 1


HUE_FACTOR: Final = 360
PERCENT_FACTOR: Final = 100


class HSB(ColorType):
    __slots__ = ('_hue', '_saturation', '_brightness')  # noqa: RUF023

    def __init__(self, hue: float, saturation: float, brightness: float) -> None:
        if not 0 <= hue <= HUE_FACTOR or not 0 <= saturation <= PERCENT_FACTOR or not 0 <= brightness <= PERCENT_FACTOR:
            raise ValueError()

        self._hue: float = hue
        self._saturation: float = saturation
        self._brightness: float = brightness

    @property
    def hue(self) -> float:
        """hue value"""
        return self._hue

    @property
    def h(self) -> float:
        """hue value"""
        return self._hue

    @property
    def saturation(self) -> float:
        """saturation value"""
        return self._saturation

    @property
    def s(self) -> float:
        """saturation value"""
        return self._saturation

    @property
    def brightness(self) -> float:
        """brightness value"""
        return self._brightness

    @property
    def b(self) -> float:
        """brightness value"""
        return self._brightness

    def replace(self, h: float | None = None, s: float | None = None, b: float | None = None,
                hue: float | None = None, saturation: float | None = None,
                brightness: float | None = None) -> Self:
        """Create a new object with (optionally) replaced values.

        :param h: New hue value
        :param hue: New hue value
        :param s: New saturation value
        :param saturation: New saturation value
        :param b: New brightness value
        :param brightness: New brightness value
        """

        if h is not None:
            if hue is not None:
                raise ValueError()
            hue = h

        if s is not None:
            if saturation is not None:
                raise ValueError()
            saturation = s

        if b is not None:
            if brightness is not None:
                raise ValueError()
            brightness = b

        return self.__class__(
            hue if hue is not None else self._hue,
            saturation if saturation is not None else self._saturation,
            brightness if brightness is not None else self._brightness,
        )

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._hue:.2f}, {self._saturation:.2f}, {self._brightness:.2f})'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._hue == other._hue and \
                self._saturation == other._saturation and \
                self._brightness == other._brightness
        return NotImplemented

    def __getitem__(self, item: int | str) -> float:
        if isinstance(item, int):
            if item == 0:
                return self._hue
            if item == 1:
                return self._saturation
            if item == 2:
                return self._brightness
            raise IndexError()

        if isinstance(item, str):
            if item in ('h', 'hue'):
                return self._hue
            if item in ('s', 'saturation'):
                return self._saturation
            if item in ('b', 'brightness'):
                return self._brightness
            raise KeyError()

        raise TypeError()

    # ------------------------------------------------------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------------------------------------------------------
    def to_rgb(self) -> RGB:
        """Create an RGB object from this object

        :return: New RGB object
        """
        return RGB.from_hsb(self)

    @classmethod
    def from_rgb(cls, obj: RGB | tuple[int, int, int]) -> Self:
        """Create an HSB object from an RGB object or an RGB tuple

        :param obj: HSB object or RGB tuple
        :return: New HSB object
        """
        if not isinstance(obj, RGB):
            obj = RGB(*obj)
        return obj.to_hsb()
