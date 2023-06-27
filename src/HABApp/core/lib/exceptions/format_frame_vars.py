import ast
import datetime
from inspect import ismodule, isclass
from pathlib import Path
from typing import List, Tuple, Callable, Any, Set

from immutables import Map
from stack_data import Variable

from HABApp.core.const.json import load_json, dump_json
from easyconfig.config_objs import ConfigObj
from .const import SEPARATOR_VARIABLES, PRE_INDENT

# don't show these types in the traceback
SKIPPED_TYPES = (
    bool, bytearray, bytes, complex, dict, float, frozenset, int, list, memoryview, set, str, tuple, type(None),
    datetime.date, datetime.datetime, datetime.time, datetime.timedelta,
    Map, Path,
)


def is_type_hint_or_type(value: Any) -> bool:
    if isinstance(value, tuple):
        return all(is_type_hint_or_type(obj) for obj in value)

    if value in SKIPPED_TYPES:
        return True

    # check if it's something from the typing module
    # we can't do that with isinstance, so we try this
    try:
        if value.__module__ == 'typing' or value.__class__.__module__ == 'typing':
            return True
    except AttributeError:
        pass

    return False


def _filter_expressions(name: str, value: Any) -> bool:
    # a is None = True
    if name.endswith(' is None'):
        return True

    return False


SKIP_VARIABLE: Tuple[Callable[[str, Any], bool], ...] = (
    # module imports
    lambda name, value: ismodule(value),

    # type hints and type tuples
    lambda name, value: is_type_hint_or_type(value),

    # functions
    lambda name, value: value is dump_json or value is load_json,

    # config value objs
    lambda name, value: isinstance(value, ConfigObj),

    # Expressions
    _filter_expressions
)

ORDER_VARIABLE: Tuple[Callable[[Variable], bool], ...] = (
    lambda x: isclass(x.value),
)


def skip_variable(var: Variable) -> bool:
    name = var.name
    value = var.value
    for func in SKIP_VARIABLE:
        if func(name, value):
            return True
    return False


def format_frame_variables(tb: List[str], stack_variables: List[Variable]):
    if not stack_variables:
        return None

    # remove variables that shall not be printed
    used_vars: List[Variable] = [v for v in stack_variables if not skip_variable(v)]

    # attributes
    dotted_names: Set[str] = {n.name.split('.')[0] for n in used_vars if '.' in n.name}

    # Sort output
    used_vars = sorted(used_vars, key=lambda x: (
        isinstance(x.nodes[0], ast.Compare),                                        # Compare objects last
        not any(map(
            lambda y: x.name == y or x.name.startswith(y + '.'), dotted_names)),    # Classes with attributes
        x.name.lower()                                                              # Name lowercase
    ))

    variables = {}

    # variables by order
    for add_var in ORDER_VARIABLE:
        for var in used_vars:
            name = var.name
            if name in variables:
                continue
            if add_var(var):
                variables[name] = var.value

    # rest of the variables
    for var in used_vars:
        if var.name not in variables:
            variables[var.name] = var.value

    if not variables:
        return None

    # Add variables to traceback
    tb.append(SEPARATOR_VARIABLES)

    for name, value in variables.items():
        tb.append(f'{" " * (PRE_INDENT + 1)}{name} = {repr(value)}')

    tb.append(SEPARATOR_VARIABLES)
