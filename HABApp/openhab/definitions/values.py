import typing
from HABApp.core.events import ComplexEventValue


class OnOffValue(ComplexEventValue):
    ON = 'ON'
    OFF = 'OFF'

    def __init__(self, value):
        super().__init__(value)
        assert value == OnOffValue.ON or value == OnOffValue.OFF, f'{value} ({type(value)})'
        self.on = value == 'ON'

    def __str__(self):
        return self.value


class PercentValue(ComplexEventValue):
    def __init__(self, value: str):
        percent = float(value)
        assert 0 <= percent <= 100, f'{percent} ({type(percent)})'
        super().__init__(percent)

    def __str__(self):
        return f'{self.value}%'


class OpenClosedValue(ComplexEventValue):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    def __init__(self, value):
        super().__init__(value)
        assert value == OpenClosedValue.OPEN or value == OpenClosedValue.CLOSED, f'{value} ({type(value)})'
        self.open = value == OpenClosedValue.OPEN

    def __str__(self):
        return self.value


class UpDownValue(ComplexEventValue):
    UP = 'UP'
    DOWN = 'DOWN'

    def __init__(self, value):
        super().__init__(value)
        assert value == UpDownValue.UP or value == UpDownValue.DOWN, f'{value} ({type(value)})'
        self.up = value == UpDownValue.UP

    def __str__(self):
        return self.value


class HSBValue(ComplexEventValue):
    def __init__(self, value: str):
        super().__init__(tuple(float(k) for k in value.split(',')))

    def __str__(self):
        return f'{self.value[0]}°,{self.value[1]}%,{self.value[2]}%'


class QuantityValue(ComplexEventValue):

    @staticmethod
    def split_unit(value: str) -> typing.Tuple[str, str]:
        p = value.rfind(' ')
        assert p >= 0, f'No unit separator found for QuantityValue in "{value}"'
        val = value[0:p]
        unit = value[p + 1:]
        return val, unit

    def __init__(self, value: str):
        value, unit = QuantityValue.split_unit(value)
        try:
            val: typing.Union[int, float] = int(value)
        except ValueError:
            val = float(value)
        super().__init__(val)
        self.unit = unit

    def __str__(self):
        return f'{self.value} {self.unit}'
