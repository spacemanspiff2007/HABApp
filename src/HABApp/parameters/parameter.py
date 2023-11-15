# ruff: noqa: TRY003, EM101
# EM101 Exception must not use a string literal, assign to variable first
# TRY003 Avoid specifying long messages outside the exception class

import typing
from math import ceil, floor

from .parameters import add_parameter as _add_parameter
from .parameters import get_value as _get_value


class BaseParameter:
    def __init__(self, filename: str, *keys, default_value: typing.Any = 'ToDo'):
        """Class to dynamically access parameters which are loaded from file.

        :param filename: filename (without extension)
        :param keys: structure in the file
        :param default_value: default value for the parameter. Is used to create the file and the structure if
                              it does not exist yet. Use ``None`` to skip creation of the file structure.
        """

        assert isinstance(filename, str), type(filename)
        self._filename: str = filename
        self._keys = keys

        # as a convenience try to create the file and the file structure
        if default_value is not None:
            _add_parameter(self._filename, *self._keys, default_value=default_value)


class Parameter(BaseParameter):

    @property
    def value(self) -> typing.Any:
        """Return the current value. This will do the lookup so make sure to not cache this value, otherwise
        the parameter might not work as expected.
        """
        return _get_value(self._filename, *self._keys)

    def __repr__(self):
        return f'<Parameter file: {self._filename}, keys: {self._keys}, value: {self.value}'

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value == other

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __ge__(self, other):
        return self.value >= other

    def __gt__(self, other):
        return self.value > other

    # https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
    # These methods are called to implement the binary arithmetic operations
    def __add__(self, other):
        return self.value.__add__(other)

    def __sub__(self, other):
        return self.value.__sub__(other)

    def __mul__(self, other):
        return self.value.__mul__(other)

    def __matmul__(self, other):
        return self.value.__matmul__(other)

    def __truediv__(self, other):
        return self.value.__truediv__(other)

    def __floordiv__(self, other):
        return self.value.__floordiv__(other)

    def __mod__(self, other):
        return self.value.__mod__(other)

    def __divmod__(self, other):
        return self.value.__divmod__(other)

    def __pow__(self, other):
        return self.value.__pow__(other)

    def __lshift__(self, other):
        return self.value.__lshift__(other)

    def __rshift__(self, other):
        return self.value.__rshift__(other)

    def __and__(self, other):
        return self.value.__and__(other)

    def __xor__(self, other):
        return self.value.__xor__(other)

    def __or__(self, other):
        return self.value.__or__(other)

    # Unary arithmetic operations (-, +, abs() and ~).
    def __neg__(self):
        return self.value.__neg__()

    def __pos__(self):
        return self.value.__pos__()

    def __abs__(self):
        return self.value.__abs__()

    def __invert__(self):
        return self.value.__invert__()

    # built-in functions complex(), int() and float().
    def __complex__(self):
        return self.value.__complex__()

    def __int__(self):
        return self.value.__int__()

    def __float__(self):
        return self.value.__float__()

    # built-in function round() and math functions trunc(), floor() and ceil().
    def __round__(self, ndigits=None):
        return self.value.__round__(ndigits)

    def __trunc__(self):
        return self.value.__trunc__()

    def __floor__(self):
        return floor(self.value)

    def __ceil__(self):
        return ceil(self.value)

    # we don't support modification in place! We have to override this because otherwise
    # python falls back to the methods above
    def __iadd__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __isub__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __imul__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __imatmul__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __itruediv__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __ifloordiv__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __imod__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __ipow__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __ilshift__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __irshift__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __iand__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __ixor__(self, other):
        raise PermissionError('Parameter can not be changed!')

    def __ior__(self, other):
        raise PermissionError('Parameter can not be changed!')


class DictParameter(BaseParameter):
    """Implements a dict interface"""

    @property
    def value(self) -> dict:
        """Return the current value. This will do the lookup so make sure to not cache this value, otherwise
        the parameter might not work as expected.
        """
        value = _get_value(self._filename, *self._keys)
        if not isinstance(value, dict):
            raise ValueError(f'Value "{value}" for {self.__class__.__name__} is not a dict! ({type(value)})')
        return value

    def __repr__(self):
        return f'<DictParameter file: {self._filename}, keys: {self._keys}, value: {self.value}'

    def __bool__(self):
        return bool(self.value)

    def __eq__(self, other):
        return self.value == other

    def __getitem__(self, item):
        return self.value[item]

    def __contains__(self, key):
        return key in self.value

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def keys(self):
        return self.value.keys()

    def values(self):
        return self.value.values()

    def items(self):
        return self.value.items()

    def get(self, item, default=None):
        return self.value.get(item, default)

    def __setitem__(self, key, value):
        raise PermissionError('Parameter can not be changed!')

    def __delitem__(self, key):
        raise PermissionError('Parameter can not be changed!')
