from easyconfig import AppConfigModel
from HABApp.config.models.location import LocationConfig
from HABApp.config.models.mqtt import MqttConfig
from HABApp.config.models.openhab import OpenhabConfig
from HABApp.config.models.directories import DirectoriesConfig
from pydantic import Field


class HABAppConfig(AppConfigModel):
    directories: DirectoriesConfig = Field(default_factory=DirectoriesConfig)
    location: LocationConfig = Field(default_factory=LocationConfig)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    openhab: OpenhabConfig = Field(default_factory=OpenhabConfig)
