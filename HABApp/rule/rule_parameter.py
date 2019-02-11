from ..runtime import Runtime


class RuleParameter:
    def __init__(self, runtime, filename, *keys):
        assert isinstance(runtime, Runtime)
        self.__runtime = runtime
        self.filename = filename
        self.keys = keys

        # as a convenience try to create the file structure
        self.__runtime.rule_params.add_param(self.filename, *self.keys)

    def get_value(self):
        return self.__runtime.rule_params.get_param(self.filename, *self.keys)

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