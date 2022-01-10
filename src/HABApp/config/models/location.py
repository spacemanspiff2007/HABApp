import logging.config

from easyconfig import ConfigModel
from pydantic import Field

import eascheduler

log = logging.getLogger('HABApp.Config')


class LocationConfig(ConfigModel):
    latitude: float = Field(default=0.0)
    longitude: float = Field(default=0.0)
    elevation: float = Field(default=0.0)

    def on_all_values_set(self):
        log.debug(f'Local Timezone: {eascheduler.const.local_tz}')
        eascheduler.set_location(self.latitude, self.longitude, self.elevation)
