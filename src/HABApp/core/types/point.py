from __future__ import annotations

from typing import Final, Literal

from geopy.distance import distance


class Point:
    __slots__ = ('_latitude', '_longitude', '_elevation')  # noqa: RUF023

    def __init__(self, latitude: float, longitude: float, elevation: float | None = None) -> None:
        if not -90 <= latitude <= 90:  # noqa: PLR2004
            msg = 'Latitude must be between -90 and 90'
            raise ValueError(msg)

        if not -180 <= longitude <= 180:  # noqa: PLR2004
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return (self._latitude == other._latitude and self._longitude == other._longitude and
                    self._elevation == other._elevation)

        return NotImplemented

    def __hash__(self) -> int:
        return hash((self._latitude, self._longitude, self._elevation))

    def is_same_point(self, other: Point | tuple[float, float, float | None] | tuple[float, float], *,
                      force_elevation_check: bool = False) -> bool:
        """Check if two points are the same.
        If one of the elevations is None only latitude and longitude is checked.

        :param other: Other point or tuple with latitude, longitude and elevation
        :param force_elevation_check: If True, elevation will always be checked even if it is None
        :return: True if the points are the same, False otherwise
        """

        try:
            other_point: Final = other if isinstance(other, Point) else Point(*other)
        except (TypeError, ValueError):
            return False

        if not force_elevation_check and (self._elevation is None or other_point._elevation is None):
            return self._latitude == other_point._latitude and self._longitude == other_point._longitude

        return (
            self._latitude == other_point._latitude and self._longitude == other_point._longitude
            and self._elevation == other_point._elevation
        )

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

    # ------------------------------------------------------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------------------------------------------------------
    def to_tuple(self) -> tuple[float, float, float | None]:
        """Create a new tuple with the values from this object

        :return: New tuple object
        """
        return self._latitude, self._longitude, self._elevation
