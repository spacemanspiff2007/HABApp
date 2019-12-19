import logging.config

import astral as _astral
import tzlocal
import voluptuous
from EasyCo import ConfigContainer, ConfigEntry

log = logging.getLogger('HABApp.Config')


class Location(ConfigContainer):
    latitude: float = ConfigEntry(default=0.0, validator=voluptuous.Any(float, int))
    longitude: float = ConfigEntry(default=0.0, validator=voluptuous.Any(float, int))
    elevation: float = ConfigEntry(default=0.0, validator=voluptuous.Any(float, int))

    def __init__(self):
        super().__init__()
        self.astral: _astral.Location = None

    def on_all_values_set(self):
        tz = tzlocal.get_localzone()
        tz_name = str(tz)
        log.debug(f'Local Timezone: {tz_name}')

        self.astral = _astral.Location()
        self.astral.name = 'HABApp'
        self.astral.latitude = self.latitude
        self.astral.longitude = self.longitude
        self.astral.elevation = self.elevation
        self.astral.timezone = tz_name
