import logging
import typing
from datetime import datetime
from math import ceil, floor

from pendulum import UTC
from pendulum import now as pd_now

from HABApp.core.const import MISSING
from HABApp.core.events import ValueChangeEvent, ValueUpdateEvent
from HABApp.core.internals import uses_post_event
from HABApp.core.items.base_item import BaseItem
from HABApp.core.lib.funcs import compare as _compare

if typing.TYPE_CHECKING:
    datetime = datetime


log = logging.getLogger('HABApp')

post_event = uses_post_event()


class BaseValueItem(BaseItem):
    """Simple item

    :ivar str name: Name of the item (read only)
    :ivar value: Value of the item, can be anything (read only)
    :ivar datetime last_change: Timestamp of the last time when the item has changed the value (read only)
    :ivar datetime last_update: Timestamp of the last time when the item has updated the value (read only)
    """

    def __init__(self, name: str, initial_value=None):
        super().__init__(name)

        self.value: typing.Any = initial_value

    def set_value(self, new_value) -> bool:
        """Set a new value without creating events on the event bus

        :param new_value: new value of the item
        :return: True if state has changed
        """
        state_changed = self.value != new_value

        _now = pd_now(UTC)
        if state_changed:
            self._last_change.set(_now)
        self._last_update.set(_now)

        self.value = new_value
        return state_changed

    def post_value(self, new_value) -> bool:
        """Set a new value and post appropriate events on the HABApp event bus
        (``ValueUpdateEvent``, ``ValueChangeEvent``)

        :param new_value: new value of the item
        :return: True if state has changed
        """
        old_value = self.value
        state_changed = self.set_value(new_value)

        # create events
        post_event(self._name, ValueUpdateEvent(self._name, self.value))
        if state_changed:
            post_event(
                self._name, ValueChangeEvent(self._name, value=self.value, old_value=old_value)
            )
        return state_changed

    def post_value_if(self, new_value, *, equal=MISSING, eq=MISSING, not_equal=MISSING, ne=MISSING,
                      lower_than=MISSING, lt=MISSING, lower_equal=MISSING, le=MISSING,
                      greater_than=MISSING, gt=MISSING, greater_equal=MISSING, ge=MISSING,
                      is_=MISSING, is_not=MISSING) -> bool:
        """
        Post a value depending on the current state of the item. If one of the comparisons is true the new state
        will be posted.

        :param new_value: new value to post
        :param equal: item state has to be equal to the passed value
        :param eq: item state has to be equal to the passed value
        :param not_equal: item state has to be not equal to the passed value
        :param ne: item state has to be not equal to the passed value
        :param lower_than: item state has to be lower than the passed value
        :param lt: item state has to be lower than the passed value
        :param lower_equal: item state has to be lower equal the passed value
        :param le: item state has to be lower equal the passed value
        :param greater_than: item state has to be greater than the passed value
        :param gt: item state has to be greater than the passed value
        :param greater_equal: item state has to be greater equal the passed value
        :param ge: item state has to be greater equal the passed value
        :param is_: item state has to be the same object as the passt value (e.g. None)
        :param is_not: item state has to be not the same object as the passt value (e.g. None)

        :return: `True` if the new value was posted else `False`
        """

        if _compare(self.value, equal=equal, eq=eq, not_equal=not_equal, ne=ne,
                    lower_than=lower_than, lt=lt, lower_equal=lower_equal, le=le,
                    greater_than=greater_than, gt=gt, greater_equal=greater_equal, ge=ge, is_=is_, is_not=is_not):
            self.post_value(new_value)
            return True
        return False

    def get_value(self, default_value=None) -> typing.Any:
        """Return the value of the item. This is a helper function that returns a default
        in case the item value is None.

        :param default_value: Return this value if the item value is None
        :return: value of the item
        """
        if self.value is None:
            return default_value
        return self.value

    def __repr__(self):
        ret = ''
        for k in ['name', 'value', 'last_change', 'last_update']:
            ret += f'{", " if ret else ""}{k}: {getattr(self, k)}'
        return f'<{self.__class__.__name__} {ret:s}>'

    # only support == and != operators by default
    # __ne__ delegates to __eq__ and inverts the result so this is not overloaded separately
    def __eq__(self, other):
        return self.value == other

    def __bool__(self):
        return bool(self.value)

    # rich comparisons
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
        if isinstance(other, BaseValueItem):
            return self.value.__add__(other.value)
        return self.value.__add__(other)

    def __sub__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__sub__(other.value)
        return self.value.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__mul__(other.value)
        return self.value.__mul__(other)

    def __matmul__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__matmul__(other.value)
        return self.value.__matmul__(other)

    def __truediv__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__truediv__(other.value)
        return self.value.__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__floordiv__(other.value)
        return self.value.__floordiv__(other)

    def __mod__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__mod__(other.value)
        return self.value.__mod__(other)

    def __divmod__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__divmod__(other.value)
        return self.value.__divmod__(other)

    def __pow__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__pow__(other.value)
        return self.value.__pow__(other)

    def __lshift__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__lshift__(other.value)
        return self.value.__lshift__(other)

    def __rshift__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__rshift__(other.value)
        return self.value.__rshift__(other)

    def __and__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__and__(other.value)
        return self.value.__and__(other)

    def __xor__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__xor__(other.value)
        return self.value.__xor__(other)

    def __or__(self, other):
        if isinstance(other, BaseValueItem):
            return self.value.__or__(other.value)
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
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __isub__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __imul__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __imatmul__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __itruediv__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __ifloordiv__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __imod__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __ipow__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __ilshift__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __irshift__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __iand__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __ixor__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')

    def __ior__(self, other):
        return PermissionError('Call not allowed! Use "set_value" or "post_value"')
