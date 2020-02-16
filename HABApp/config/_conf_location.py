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

        self._astral_location: _astral.LocationInfo
        self.astral_observer: _astral.Observer

    def on_all_values_set(self):
        tz = tzlocal.get_localzone()
        tz_name = str(tz)
        log.debug(f'Local Timezone: {tz_name}')

        # unsure why we need the location in 2.1
        self._astral_location = _astral.LocationInfo(name='HABApp', )
        self._astral_location.latitude = self.latitude
        self._astral_location.longitude = self.longitude
        self._astral_location.timezone = tz_name

        self.astral_observer = self._astral_location.observer
        self.astral_observer.elevation = self.elevation
