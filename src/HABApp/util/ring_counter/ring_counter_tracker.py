from typing import Final, Literal


class RingCounterTracker:
    """Class that tracks a ring counter value and only allows increasing or decreasing values.
    """

    __slots__ = ('_ignore', '_is_increasing', '_last_value', '_max_value', '_min_value')

    def __init__(self, min_value: int | None = None, max_value: int | None = None, *,
                 ignore: int = 10, direction: Literal['increasing', 'decreasing'] = 'increasing') -> None:
        """

        :param min_value: Minimum value of the ring counter
        :param max_value: Maximum value of the ring counter
        :param ignore: How many values to ignore before allowing a lower value
        :param direction: Direction of the counter: increasing or decreasing
        """
        if max_value is None:
            max_value = min_value
            min_value = 0

        if not isinstance(min_value, int):
            msg = 'Min value must be an integer'
            raise TypeError(msg)
        if not isinstance(max_value, int):
            msg = 'Max value must be an integer'
            raise TypeError(msg)
        if not isinstance(ignore, int):
            msg = 'Ignore value must be an integer'
            raise TypeError(msg)

        if not min_value < max_value:
            msg = f'Min value {min_value} must be less than max value {max_value}'
            raise ValueError(msg)
        if not 0 < ignore < (max_value - min_value + 1):
            msg = f'Ignore value {ignore} must be greater than 0 and lower than max value {max_value}'
            raise ValueError(msg)

        self._min_value: Final = min_value
        self._max_value: Final = max_value
        self._ignore: Final = ignore
        self._is_increasing: Final = direction != 'decreasing'

        # # initialize so we always allow on first call
        self._last_value: int  = (max_value + ignore + 2) if self._is_increasing else (min_value - ignore - 2)

    @property
    def value(self) -> int:
        """Get the last value of the ring counter."""
        return self._last_value

    def __int__(self) -> int:
        return self._last_value

    def allow(self, value: int, *, strict: bool = True, set_value: bool = True) -> bool:
        """Return if a value is allowed and set it as the current value if it was allowed.

        :param value: Value to be checked
        :param strict: Check if the value is within min/max and of correct type
        :param set_value: Set the new value as the current value if it was allowed
        :return: True if the value was allowed, False if not
        """
        if strict and not isinstance(value, int):
            msg = f'Value must be an integer (is {type(value)})'
            raise TypeError(msg)

        if value > (max_value := self._max_value):
            if strict:
                msg = f'Value {value} is greater than max value {self._max_value}'
                raise ValueError(msg)
            return False

        if value < (min_value := self._min_value):
            if strict:
                msg = f'Value {value} is less than min value {self._min_value}'
                raise ValueError(msg)
            return False

        if self._is_increasing:
            lowest_ignored = (last_value := self._last_value) - self._ignore + 1
            if lowest_ignored <= value <= last_value:
                return False
            if lowest_ignored < min_value:
                lowest_ignored += (max_value - min_value + 1)
                if lowest_ignored <= value <= max_value:
                    return False
        else:
            highest_ignored = (last_value := self._last_value) + self._ignore - 1
            if last_value <= value <= highest_ignored:
                return False
            if highest_ignored > max_value:
                highest_ignored -= (max_value - min_value + 1)
                if min_value <= value <= highest_ignored:
                    return False

        if set_value:
            self._last_value = value
        return True

    def test_allow(self, value: int) -> bool:
        """Test if a value will be allowed without setting it as the current value.

        :param value: value to test
        :return: True if the value would be allowed, False if not
        """
        return self.allow(value, strict=False, set_value=False)

    def __repr__(self) -> str:
        value = self._last_value
        if value > self._max_value or value < self._min_value:
            value = '-'
        return (f'{self.__class__.__name__:s}(value={value}, '
                f'min={self._min_value:d}, max={self._max_value:d}, ignore={self._ignore:d})')

    def __eq__(self, other: int) -> bool:
        return self._last_value == other

    def __ne__(self, other: float) -> bool:
        return self._last_value != other

    def __ge__(self, other: float) -> bool:
        return self._last_value >= other

    def __gt__(self, other: float) -> bool:
        return self._last_value > other

    def __le__(self, other: float) -> bool:
        return self._last_value <= other

    def __lt__(self, other: float) -> bool:
        return self._last_value < other
