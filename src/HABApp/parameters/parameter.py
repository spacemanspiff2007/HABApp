# ruff: noqa: TRY003, EM101
# EM101 Exception must not use a string literal, assign to variable first
# TRY003 Avoid specifying long messages outside the exception class

from math import ceil, floor
from typing import Any, Final

from pydantic import BaseModel

from HABApp.core.provider import HABAPP_PROVIDER
from HABApp.parameters.registry import ParameterRegistry


class BaseParameter:
    __slots__ = ('_filename', '_keys', '_registry')

    def __init__(self, filename: str, *keys: str | float, default_value: Any = 'ToDo') -> None:
        """Class to dynamically access parameters which are loaded from file.

        :param filename: filename (without extension)
        :param keys: structure in the file
        :param default_value: default value for the parameter. Is used to create the file and the structure if
                              it does not exist yet. Use ``None`` to skip creation of the file structure.
        """

        if not isinstance(filename, str):
            msg = f'filename must be a str, got {type(filename)}'
            raise TypeError(msg)

        self._filename: Final = filename
        self._keys: Final = keys
        self._registry: Final = HABAPP_PROVIDER.get_existing(ParameterRegistry)

        # as a convenience try to create the file and the file structure
        if default_value is not None:
            self._registry.add_parameter(self._filename, *self._keys, default_value=default_value)


class Parameter[T](BaseParameter):  # noqa: PLW1641
    __slots__ = ('_type',)

    def __init__(self, filename: str, *keys: str | float, value_type: type[T] | tuple[type[T], ...] = object,
                 default_value: Any = 'ToDo') -> None:
        """
        :param filename: filename (without extension)
        :param keys: structure in the file
        :param value_type: type (or tuple of types) the value has to be an instance of.
                           Use ``object`` (default) to skip the check.
        :param default_value: default value for the parameter. Is used to create the file and the structure if
                              it does not exist yet. Use ``None`` to skip creation of the file structure.
        """
        super().__init__(filename, *keys, default_value=default_value)
        self._type: Final = value_type

    @property
    def value(self) -> T:
        """Return the current value. This will do the lookup so make sure to not cache this value, otherwise
        the parameter might not work as expected.
        """
        value = self._registry.get_value(self._filename, *self._keys)
        if not isinstance(value, self._type):
            msg = f'Value "{value}" for {self.__class__.__name__} is not of type {self._type}! ({type(value)})'
            raise TypeError(msg)
        return value

    def __repr__(self) -> str:
        return f'<Parameter file: {self._filename}, keys: {self._keys}, value: {self.value}'

    def __bool__(self) -> bool:
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
    def __complex__(self) -> complex:
        return self.value.__complex__()

    def __int__(self) -> int:
        return self.value.__int__()

    def __float__(self) -> float:
        return self.value.__float__()

    # built-in function round() and math functions trunc(), floor() and ceil().
    def __round__(self, ndigits: int | None = None):
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


class StrParameter(Parameter[str]):
    """:class:`Parameter` that is typed to always return a ``str`` value."""

    __slots__ = ()

    def __init__(self, filename: str, *keys: str | float, default_value: Any = 'ToDo') -> None:
        super().__init__(filename, *keys, value_type=str, default_value=default_value)


class IntParameter(Parameter[int]):
    """:class:`Parameter` that is typed to always return an ``int`` value."""

    __slots__ = ()

    def __init__(self, filename: str, *keys: str | float, default_value: Any = 'ToDo') -> None:
        super().__init__(filename, *keys, value_type=int, default_value=default_value)


class FloatParameter(Parameter[float]):
    """:class:`Parameter` that is typed to always return a ``float`` value."""

    __slots__ = ()

    def __init__(self, filename: str, *keys: str | float, default_value: Any = 'ToDo') -> None:
        super().__init__(filename, *keys, value_type=float, default_value=default_value)


class NumberParameter(Parameter[int | float]):
    """:class:`Parameter` that is typed to always return an ``int`` or ``float`` value. The value is
    returned as-is, i.e. it is not converted to a common type.
    """

    __slots__ = ()

    def __init__(self, filename: str, *keys: str | float, default_value: Any = 'ToDo') -> None:
        super().__init__(filename, *keys, value_type=(int, float), default_value=default_value)


class DictParameter(BaseParameter):
    """Implements a dict interface"""

    __slots__ = ()

    @property
    def value(self) -> dict:
        """Return the current value. This will do the lookup so make sure to not cache this value, otherwise
        the parameter might not work as expected.
        """
        value = self._registry.get_value(self._filename, *self._keys)
        if not isinstance(value, dict):
            msg = f'Value "{value}" for {self.__class__.__name__} is not a dict! ({type(value)})'
            raise TypeError(msg)
        return value

    def __repr__(self) -> str:
        return f'<DictParameter file: {self._filename}, keys: {self._keys}, value: {self.value}'

    def __bool__(self) -> bool:
        return bool(self.value)

    def __eq__(self, other):
        return self.value == other

    def __getitem__(self, item):
        return self.value[item]

    def __contains__(self, key) -> bool:
        return key in self.value

    def __iter__(self):
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def keys(self):
        return self.value.keys()

    def values(self):
        return self.value.values()

    def items(self):
        return self.value.items()

    def get(self, item, default=None):
        return self.value.get(item, default)

    def __setitem__(self, key, value) -> None:
        raise PermissionError('Parameter can not be changed!')

    def __delitem__(self, key) -> None:
        raise PermissionError('Parameter can not be changed!')


class BaseModelParameter[T: BaseModel](BaseParameter):
    """Parameter that validates the value at the given path against a pydantic model and returns
    a validated model instance.

    Unlike :class:`set_file_validator` (which validates the whole file once, when it is loaded) this
    validates only the value found at ``keys`` - and does so on every access. This makes it possible to
    use different (sub-)models for different parts of the same file, independent of (and in addition to)
    a whole-file validator.
    """

    __slots__ = ('_model', )

    def __init__(self, filename: str, *keys: str | float, model: type[T],
                 default_value: Any = None) -> None:
        """
        :param filename: filename (without extension)
        :param keys: structure in the file
        :param model: pydantic model that describes (and validates) the value found at ``keys``
        :param default_value: default value for the parameter, see ``BaseParameter``. Since ``model`` typically
                              already describes required fields and their defaults use ``None`` (default) to
                              skip the automatic creation of the file structure. Pass a plain ``dict`` matching
                              ``model`` if the structure should be created automatically instead.
        """
        super().__init__(filename, *keys, default_value=default_value)
        self._model: Final = model

    @property
    def value(self) -> T:
        """Validate the current raw value against the configured model and return the resulting model instance.
        This will do the lookup (and validation) so make sure to not cache this value, otherwise
        the parameter might not work as expected.
        """
        raw = self._registry.get_value(self._filename, *self._keys)
        return self._model.model_validate(raw)

    def __repr__(self) -> str:
        return f'<BaseModelParameter file: {self._filename}, keys: {self._keys}, model: {self._model.__name__}>'
