import logging.config

from pydantic import Field

from easyconfig import BaseModel

log = logging.getLogger('HABApp.Config')


class LocationConfig(BaseModel):
    """location where the instance is running. Is used to calculate Sunrise/Sunset."""

    latitude: float = Field(default=0.0)
    longitude: float = Field(default=0.0)
    elevation: float = Field(default=0.0)
