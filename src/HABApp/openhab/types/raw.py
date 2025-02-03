from __future__ import annotations

from typing import Final

from typing_extensions import Self


class RawType:
    __slots__ = ('_type', '_data')  # noqa: RUF023

    def __init__(self, type: str, data: bytes) -> None:  # noqa: A002
        self._type: Final = type
        self._data: Final = data

    @property
    def type(self) -> str:
        return self._type

    @property
    def data(self) -> bytes:
        return self._data

    def __str__(self) -> str:
        data = self._data

        unit = 'kiB'
        size = len(self.data) / 1024
        if size > 1024:
            unit = 'MiB'
            size /= 1024
        fmt = '.1f' if size < 10 else '.0f'
        return (f'{self.__class__.__name__}(type={self._type:s} '
                f'data={data[:5].hex():s}..{data[-5:].hex():s} ({size:{fmt:s}}{unit}))')

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._type == other._type and self._data == other._data
        if isinstance(other, bytes):
            return self._data == other
        return NotImplemented

    @classmethod
    def create(cls, type: str, data: bytes) -> Self:  # noqa: A002

        # Remove MIME type prefix for common image file types
        # https://developer.mozilla.org/en-US/docs/Web/Media/Formats/Image_types
        if type.endswith(('apng', 'avif', 'gif', 'jpeg', 'png', 'svg', 'webp', 'bmp', 'x-icon', 'tiff')):
            type = type.removeprefix('image/')

        return cls(type, data)
