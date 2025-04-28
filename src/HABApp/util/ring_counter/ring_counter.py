from typing import Final

from typing_extensions import Self


class RingCounter:
    """A ring counter is a counter that wraps around when it reaches its maximum value.
    """

    __slots__ = ('_max_value', '_min_value', '_value')

    def __init__(self, min_value: int | None = None, max_value: int | None = None, *,
                 initial_value: int | None = None) -> None:
        if max_value is None:
            max_value = min_value
            min_value = 0

        if initial_value is None:
            initial_value = min_value

        if not isinstance(min_value, int):
            msg = 'Min value must be an integer'
            raise TypeError(msg)
        if not isinstance(max_value, int):
            msg = 'Max value must be an integer'
            raise TypeError(msg)
        if not isinstance(initial_value, int):
            msg = 'Initial value must be an integer'
            raise TypeError(msg)

        if not min_value < max_value:
            msg = f'Min value {min_value} must be less than max value {max_value}'
            raise ValueError(msg)
        if not min_value <= initial_value <= max_value:
            msg = f'Initial value {initial_value} is not in range [{min_value:d}..{max_value:d}]'
            raise ValueError(msg)

        self._min_value: Final = min_value
        self._max_value: Final = max_value
        self._value: int = initial_value

    @property
    def size(self) -> int:
        """Return the size (how man values it can count) of the ring counter."""
        return self._max_value - self._min_value + 1

    def __len__(self) -> int:
        return self.size

    @property
    def value(self) -> int:
        """Current value of the ring counter."""
        return self._value

    def __int__(self) -> int:
        return self._value

    def increase(self, value: int = 1) -> Self:
        """Increase the value of the ring counter by the given value.

        :param value: How much to increase the value by.
        """
        if value < 0:
            msg = 'Value must be >= 0'
            raise ValueError(msg)

        self._value += value

        while self._value > self._max_value:
            self._value -= self.size

        return self

    def decrease(self, value: int = 1) -> Self:
        """Decrease the value of the ring counter by the given value.

        :param value: How much to decrease the value by.
        """
        if value < 0:
            msg = 'Value must be >= 0'
            raise ValueError(msg)

        self._value -= value

        while self._value < self._min_value:
            self._value += self.size

        return self

    def __iadd__(self, other: int) -> Self:
        return self.increase(other)

    def __isub__(self, other: int) -> Self:
        return self.decrease(other)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(value={self._value:d}, min={self._min_value:d} max={self._max_value:d})'

    def __eq__(self, other: int) -> bool:
        return self._value == other

    def __ne__(self, other: float) -> bool:
        return self._value != other

    def __ge__(self, other: float) -> bool:
        return self._value >= other

    def __gt__(self, other: float) -> bool:
        return self._value > other

    def __le__(self, other: float) -> bool:
        return self._value <= other

    def __lt__(self, other: float) -> bool:
        return self._value < other
