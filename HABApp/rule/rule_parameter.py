import typing

from ..rule_manager import RuleParameters


class RuleParameter:
    def __init__(self, rule_parameters: RuleParameters, filename: str, *keys, default_value: typing.Any = 'ToDo'):

        assert isinstance(rule_parameters, RuleParameters), type(rule_parameters)
        self.__parameters: RuleParameters = rule_parameters

        assert isinstance(filename, str)
        self.filename: str = filename
        self.keys = keys

        # as a convenience try to create the file and the file structure
        self.__parameters.add_param(self.filename, *self.keys, default_value=default_value)

    def get_value(self):
        return self.__parameters.get_param(self.filename, *self.keys)

    def __eq__(self, other):
        return self.get_value() == other

    def __ne__(self, other):
        return self.get_value() != other

    def __lt__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.get_value() < other

    def __le__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.get_value() <= other

    def __ge__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.get_value() >= other

    def __gt__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented

        return self.get_value() > other

    def __repr__(self):
        return f'<RuleParameter file: {self.filename}, keys: {self.keys}, ' \
               f'value: {self.get_value()}'
