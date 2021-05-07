import logging.config

import eascheduler
import voluptuous
from EasyCo import ConfigContainer, ConfigEntry

log = logging.getLogger('HABApp.Config')


class Location(ConfigContainer):
    latitude: float = ConfigEntry(default=0.0, validator=voluptuous.Any(float, int))
    longitude: float = ConfigEntry(default=0.0, validator=voluptuous.Any(float, int))
    elevation: float = ConfigEntry(default=0.0, validator=voluptuous.Any(float, int))

    def __init__(self):
        super().__init__()

    def on_all_values_set(self):
        log.debug(f'Local Timezone: {eascheduler.const.local_tz}')
        eascheduler.set_location(self.latitude, self.longitude, self.elevation)
