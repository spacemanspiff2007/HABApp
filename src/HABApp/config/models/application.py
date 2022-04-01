from easyconfig import AppBaseModel
from HABApp.config.models.location import LocationConfig
from HABApp.config.models.mqtt import MqttConfig
from HABApp.config.models.openhab import OpenhabConfig
from HABApp.config.models.habapp import HABAppConfig
from HABApp.config.models.directories import DirectoriesConfig
from pydantic import Field


class ApplicationConfig(AppBaseModel):
    """Structure that contains the complete configuration"""

    directories: DirectoriesConfig = Field(default_factory=DirectoriesConfig)
    location: LocationConfig = Field(default_factory=LocationConfig)
    mqtt: MqttConfig = Field(default_factory=MqttConfig)
    openhab: OpenhabConfig = Field(default_factory=OpenhabConfig)
    habapp: HABAppConfig = Field(default_factory=HABAppConfig, in_file=False)
