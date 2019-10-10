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
        value = float(value)
        assert 0 <= value <= 100, f'{value} ({type(value)})'
        super().__init__(value)

    def __str__(self):
        return f'{self.value}%'


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
    def __init__(self, value: str):
        val, unit = value.split(' ')
        try:
            val = int(val)
        except ValueError:
            val = float(val)

        super().__init__(val)
        self.unit = unit

    def __str__(self):
        return f'{self.value} {self.unit}'
