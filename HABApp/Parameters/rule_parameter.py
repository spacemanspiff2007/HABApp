import typing

from .parameters import add_parameter as _add_parameter
from .parameters import get_value as _get_value


class RuleParameter:
    def __init__(self, filename: str, *keys, default_value: typing.Any = 'ToDo'):

        assert isinstance(filename, str)
        self.filename: str = filename
        self.keys = keys

        # as a convenience try to create the file and the file structure
        _add_parameter(self.filename, *self.keys, default_value=default_value)

    @property
    def value(self):
        return _get_value(self.filename, *self.keys)

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.value < other

    def __le__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.value <= other

    def __ge__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.value >= other

    def __gt__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.value > other

    def __repr__(self):
        return f'<RuleParameter file: {self.filename}, keys: {self.keys}, value: {self.value}'

    def __str__(self):
        return str(self.value)


def get_parameter(filename: str, *keys, default_value: typing.Any = 'ToDo') -> RuleParameter:
    return RuleParameter(filename, *keys, default_value=default_value)


def get_parameter_value(filename: str, *keys, default_value: typing.Any = 'ToDo') -> typing.Any:
    return RuleParameter(filename, *keys, default_value=default_value).value
