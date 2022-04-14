from inspect import ismodule, isclass
from typing import List, Tuple, Callable, Any

from immutables import Map
from stack_data import Variable

from HABApp.core.const.json import load_json, dump_json
from .const import SEPARATOR_VARIABLES, PRE_INDENT


def _filter_expressions(name: str, value: Any) -> bool:
    # a is None = True
    if name.endswith(' is None'):
        return True

    # These types show no explicit types
    skipped_types = (type(None), str, float, int, list, dict, set, frozenset, Map)

    # type(b) = <class 'NoneType'>
    if name.startswith('type(') and value in skipped_types:
        return True

    # (str, int) = (<class 'str'>, <class 'int'>)
    if name.startswith('(') and name.endswith(')') and isinstance(value, tuple) and all(
            map(lambda x: x in skipped_types, value)):
        return True

    return False


SKIP_VARIABLE: Tuple[Callable[[str, Any], bool], ...] = (
    # module imports
    lambda name, value: ismodule(value),
    # type hints
    lambda name, value: name.startswith('typing.'),
    # functions
    lambda name, value: value is dump_json or value is load_json,

    # Expressions
    _filter_expressions
)

ORDER_VARIABLE: Tuple[Callable[[str, Any], bool], ...] = (
    lambda name, value: isclass(value),
)


def skip_variable(var: Variable) -> bool:
    for func in SKIP_VARIABLE:
        name = var.name
        value = var.value
        if func(name, value):
            return True
    return False


def format_frame_variables(tb: List[str], stack_variables: List[Variable]):
    if not stack_variables:
        return None

    tb.append(SEPARATOR_VARIABLES)

    # remove variables that shall not be printed
    used_vars: List[Variable] = [v for v in stack_variables if not skip_variable(v)]
    # sort alphabetically
    used_vars = sorted(used_vars, key=lambda x: x.name)

    variables = {}

    # variables by order
    for add_var in ORDER_VARIABLE:
        for var in used_vars:
            name = var.name
            value = var.value
            if name in variables:
                continue
            if add_var(name, value):
                variables[name] = value

    # rest of the variables
    for var in used_vars:
        if var.name not in variables:
            variables[var.name] = var.value

    for name, value in variables.items():
        tb.append(f'{" " * (PRE_INDENT + 1)}{name} = {repr(value)}')

    tb.append(SEPARATOR_VARIABLES)
