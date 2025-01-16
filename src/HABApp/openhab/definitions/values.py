from typing import Final, Literal, override

from typing_extensions import Self

from HABApp.core.events import ComplexEventValue
from HABApp.openhab.definitions import (
    OnOffType,
    OpenClosedType,
    PercentType,
    PointType,
    QuantityType,
    RawType,
    UpDownType,
)


class ComplexOhValue(ComplexEventValue):
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        raise NotImplementedError()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ComplexOhValue):
            return NotImplemented
        return self.value == other.value


ON: Final = OnOffType.ON
OFF: Final = OnOffType.OFF


class OnOffValue(ComplexOhValue):
    value: Literal['ON', 'OFF']

    def __init__(self, value: Literal['ON', 'OFF']) -> None:
        super().__init__(value)
        self.is_on = value == ON
        self.is_off = value == OFF

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(OnOffType.from_oh_str(state))

    def __str__(self) -> str:
        return self.value


class PercentValue(ComplexOhValue):
    value: float

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(PercentType.from_oh_str(state))

    def __str__(self) -> str:
        return f'{self.value}%'


OPEN: Final = OpenClosedType.OPEN
CLOSED: Final = OpenClosedType.CLOSED


class OpenClosedValue(ComplexOhValue):
    value: Literal['OPEN', 'CLOSED']

    def __init__(self, value: Literal['OPEN', 'CLOSED']) -> None:
        super().__init__(value)
        self.is_open = value == OPEN
        self.is_closed = value == CLOSED

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(OpenClosedType.from_oh_str(state))

    def __str__(self) -> str:
        return self.value


UP: Final = UpDownType.UP
DOWN: Final = UpDownType.DOWN


class UpDownValue(ComplexOhValue):
    value: Literal['UP', 'DOWN']

    def __init__(self, value: Literal['UP', 'DOWN']) -> None:
        super().__init__(value)
        self.is_up = value == UpDownType.UP
        self.is_down = value == UpDownType.DOWN

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(UpDownType.from_oh_str(state))

    def __str__(self) -> str:
        return self.value


class PointValue(ComplexOhValue):
    value: tuple[float, float, float | None]

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(PointType.from_oh_str(state))

    def __str__(self) -> str:
        a, b, c = self.value
        return f'{a},{b},{c}' if c is not None else f'{a},{b}'


class QuantityValue(ComplexOhValue):
    value: int | float

    def __init__(self, value: tuple[int | float, str]) -> None:
        value, unit = value
        super().__init__(value)
        self.unit: Final = unit

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(QuantityType.from_oh_str(state))

    def __str__(self) -> str:
        return f'{self.value} {self.unit:s}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuantityValue):
            return NotImplemented
        return self.value == other.value and self.unit == other.unit


class RawValue(ComplexOhValue):
    value: bytes

    def __init__(self, value: tuple[str, bytes]) -> None:
        data_type, data_bytes = value
        super().__init__(data_bytes)
        self.type: Final = data_type

    @override
    @classmethod
    def from_oh_str(cls, state: str) -> Self:
        return cls(RawType.from_oh_str(state))

    def __str__(self) -> str:
        return f'{self.type:s}'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RawValue):
            return self.value == other.value and self.type == other.type
        if isinstance(other, bytes):
            return self.value == other
        return NotImplemented


ALL_VALUES: Final[tuple[type[ComplexOhValue], ...]] = (
    OnOffValue,
    PercentValue,
    OpenClosedValue,
    UpDownValue,
    PointValue,
    QuantityValue,
    RawValue
)
