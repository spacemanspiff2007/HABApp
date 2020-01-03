from HABApp.core.items import ColorItem as ColorItemCore
from .commands import OnOffCommand, PercentCommand
from ..definitions import OnOffValue, PercentValue, HSBValue


class ColorItem(ColorItemCore, OnOffCommand, PercentCommand):

    def set_value(self, hue=0.0, saturation=0.0, brightness=0.0):

        if isinstance(hue, OnOffValue):
            return super().set_value(hue=None, saturation=None, brightness=100 if hue.on else 0)
        elif isinstance(hue, PercentValue):
            return super().set_value(hue=None, saturation=None, brightness=hue.value)
        elif isinstance(hue, HSBValue):
            return super().set_value(hue=hue.value)

        return super().set_value(hue=hue, saturation=saturation, brightness=brightness)

    def __str__(self):
        return self.value

    def is_on(self) -> bool:
        return self.brightness > 0
    
    def is_off(self) -> bool:
        return self.brightness <= 0
