from typing import FrozenSet, Mapping, Optional, Tuple

from immutables import Map

from HABApp.core.lib import hsb_to_rgb, rgb_to_hsb
from HABApp.openhab.items.base_item import MetaData, OpenhabItem
from HABApp.openhab.items.commands import OnOffCommand, PercentCommand
from ..definitions import HSBValue, OnOffValue, PercentValue

HUE_FACTOR = 360
PERCENT_FACTOR = 100


class ColorItem(OpenhabItem, OnOffCommand, PercentCommand):
    """ColorItem which accepts and converts the data types from OpenHAB

    :ivar str name: |oh_item_desc_name|
    :ivar Tuple[float, float, float] value: |oh_item_desc_value|
    :ivar float hue: Hue part of the value
    :ivar float saturation: Saturation part of the value
    :ivar float brightness: Brightness part of the value

    :ivar Optional[str] label: |oh_item_desc_label|
    :ivar FrozenSet[str] tags: |oh_item_desc_tags|
    :ivar FrozenSet[str] groups: |oh_item_desc_group|
    :ivar Mapping[str, MetaData] metadata: |oh_item_desc_metadata|
    """

    def __init__(self, name: str, h: float = 0.0, s: float = 0.0, b: float = 0.0,
                 label: Optional[str] = None, tags: FrozenSet[str] = frozenset(), groups: FrozenSet[str] = frozenset(),
                 metadata: Mapping[str, MetaData] = Map()):
        super().__init__(name=name, initial_value=(h, s, b), label=label, tags=tags, groups=groups, metadata=metadata)

        self.hue: float = min(max(0.0, h), HUE_FACTOR)
        self.saturation: float = min(max(0.0, s), PERCENT_FACTOR)
        self.brightness: float = min(max(0.0, b), PERCENT_FACTOR)

    @staticmethod
    def _state_from_oh_str(state: str) -> Tuple[float, float, float]:
        h, s, b = state.split(',')
        return float(h), float(s), float(b)

    @classmethod
    def from_oh(cls, name: str, value=None, label: Optional[str] = None, tags: FrozenSet[str] = frozenset(),
                groups: FrozenSet[str] = frozenset(), metadata: Mapping[str, MetaData] = Map()):
        if value is None:
            return cls(name, label=label, tags=tags, groups=groups, metadata=metadata)
        return cls(
            name, *cls._state_from_oh_str(value), label=label, tags=tags, groups=groups, metadata=metadata)

    def set_value(self, hue=0.0, saturation=0.0, brightness=0.0):
        """Set the color value

        :param hue: hue (in °)
        :param saturation: saturation (in %)
        :param brightness: brightness (in %)
        """

        if isinstance(hue, OnOffValue):
            brightness = 100 if hue.on else 0
            saturation = None
            hue = None
        elif isinstance(hue, PercentValue):
            brightness = hue.value
            saturation = None
            hue = None
        elif isinstance(hue, HSBValue):
            hue, saturation, brightness = hue.value
        elif isinstance(hue, tuple):
            # map tuples to variables e.g. when calling post_value
            # when processing events instead of three values we get the tuple
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

    def get_rgb(self, max_rgb_value=255) -> Tuple[int, int, int]:
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
