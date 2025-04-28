import operator as _operator
from collections.abc import Callable
from typing import Any, Final

from HABApp.core.const import MISSING


CMP_OPS: Final[dict[str, Callable[[Any, Any], bool]]] = {
    'lt': _operator.lt, 'lower_than': _operator.lt,
    'le': _operator.le, 'lower_equal': _operator.le,
    'eq': _operator.eq, 'equal': _operator.eq,
    'ne': _operator.ne, 'not_equal': _operator.ne,
    'gt': _operator.gt, 'greater_than': _operator.gt,
    'ge': _operator.ge, 'greater_equal': _operator.ge,

    'is_': _operator.is_,
    'is_not': _operator.is_not,
}


def compare(value: Any, **kwargs) -> bool:

    for name, cmp_value in kwargs.items():
        if cmp_value is MISSING:
            continue
        if CMP_OPS[name](value, cmp_value):
            return True
    return False
