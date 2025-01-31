from __future__ import annotations

from typing import Final, Literal

from geopy.distance import distance
from typing_extensions import Self


class Point:
    __slots__ = ('_latitude', '_longitude', '_elevation')  # noqa: RUF023

    def __init__(self, latitude: float, longitude: float, elevation: float | None = None) -> None:
        if not -90 <= latitude <= 90:
            msg = 'Latitude must be between -90 and 90'
            raise ValueError(msg)

        if not -180 <= longitude <= 180:
            msg = 'Longitude must be between -180 and 180'
            raise ValueError(msg)

        if elevation is not None and not isinstance(elevation, (float, int)):
            msg = 'Elevation must be int or float'
            raise TypeError(msg)

        self._latitude: Final = latitude
        self._longitude: Final = longitude
        self._elevation: Final = elevation

    @property
    def latitude(self) -> float:
        """Latitude of the point"""
        return self._latitude

    @property
    def longitude(self) -> float:
        """Longitude of the point"""
        return self._longitude

    @property
    def elevation(self) -> float | None:
        """Elevation of the point"""
        return self._elevation

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._latitude}, {self._longitude}, {self._elevation})'

    def distance(self, other: Point | tuple[float, float, float | None] | tuple[float, float], *,
                 unit: Literal['km', 'kilometers', 'meters', 'm', 'miles', 'mi', 'feet', 'fi'] = 'kilometers') -> float:
        """Calculate the distance between two points

        :param other: Other point or tuple with latitude, longitude and elevation
        :param unit: unit in which the distance should be returned
        :return: distance
        """

        if isinstance(other, Point):
            d = distance((self._latitude, self._longitude), (other._latitude, other._longitude))
            return getattr(d, unit)

        if isinstance(other, tuple) and len(other) in (2, 3):
            return self.distance(Point(*other), unit=unit)

        raise ValueError()

    def __eq__(self, other: Self | tuple[float, float, float | None] | tuple[float, float]) -> bool:
        if isinstance(other, self.__class__):
            return (self._latitude == other._latitude and self._longitude == other._longitude and
                    self._elevation == other._elevation)

        if isinstance(other, tuple):
            # compare directly with tuple so we don't raise and exception
            match len(other):
                case 2:
                    lat, long = other
                    return self._latitude == lat and self._longitude == long and self._elevation is None
                case 3:
                    lat, long, elev = other
                    return self._latitude == lat and self._longitude == long and self._elevation == elev

        return NotImplemented

    def __getitem__(self, item: int | str) -> float:
        if isinstance(item, int):
            if item == 0:
                return self._latitude
            if item == 1:
                return self._longitude
            if item == 2:
                return self._elevation
            raise IndexError()

        if isinstance(item, str):
            if item in ('lat', 'latitude'):
                return self._latitude
            if item in ('long', 'longitude'):
                return self._longitude
            if item in ('elev', 'elevation'):
                return self._elevation
            raise KeyError()

        raise TypeError()
