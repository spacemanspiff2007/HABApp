from easyconfig import BaseModel
from pydantic import Field


class LocationConfig(BaseModel):
    """location where the instance is running. Is used to calculate Sunrise/Sunset and holidays."""

    latitude: float = Field(default=0.0)
    longitude: float = Field(default=0.0)
    elevation: float = Field(default=0.0)

    country: str = Field(default='', description='ISO 3166-1 Alpha-2 country code')
    subdivision: str = Field(
        default='', description='The subdivision (e.g. state or province) as a ISO 3166-2 code or its alias')
