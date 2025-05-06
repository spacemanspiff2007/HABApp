import ast
import datetime
import importlib
from collections.abc import Callable
from inspect import isclass, ismodule
from pathlib import Path
from typing import Any, Final

import whenever
from easyconfig.config_objs import ConfigObj
from immutables import Map
from stack_data import Variable

from HABApp.core.const.json import dump_json, load_json

from .const import PRE_INDENT, SEPARATOR_VARIABLES


# don't show these types in the traceback
SKIPPED_TYPES = (
    bool, bytearray, bytes, complex, dict, float, frozenset, int, list, memoryview, set, str, tuple, type(None),
    datetime.date, datetime.datetime, datetime.time, datetime.timedelta,
    Map, Path,
    whenever.Instant,
    whenever.SystemDateTime, whenever.PlainDateTime, whenever.ZonedDateTime, whenever.OffsetDateTime,
    whenever.TimeDelta, whenever.DateDelta, whenever.DateTimeDelta
)


def is_type_hint_or_type(value: Any) -> bool:
    if isinstance(value, tuple):
        return all(is_type_hint_or_type(obj) for obj in value)

    # compare through identity since some objects override the equality operator.
    # If we check with "value in SKIPPED_TYPES" we might get an exception because there the __eq__ operator is used
    if any(value is o for o in SKIPPED_TYPES):
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


SKIPPED_OBJS: Final[tuple[str, ...]] = (
    'HABApp.core.Items',
)


def _skip_objs(name: str, value: Any) -> bool:
    for dotted_path in SKIPPED_OBJS:
        path = dotted_path.split('.')
        obj = importlib.import_module('.'.join(path[:-1]))
        if value is getattr(obj, path[-1]):
            return True
    return False


SKIP_VARIABLE: tuple[Callable[[str, Any], bool], ...] = (
    # module imports
    lambda name, value: ismodule(value),

    # type hints and type tuples
    lambda name, value: is_type_hint_or_type(value),

    # functions
    lambda name, value: value is dump_json or value is load_json,

    # config value objs
    lambda name, value: isinstance(value, ConfigObj),

    # Expressions
    _filter_expressions,
)

ORDER_VARIABLE: tuple[Callable[[Variable], bool], ...] = (
    lambda x: isclass(x.value),
)


def skip_variable(var: Variable) -> bool:
    name = var.name
    value = var.value
    return any(func(name, value) for func in SKIP_VARIABLE)


def format_frame_variables(tb: list[str], stack_variables: list[Variable]):
    if not stack_variables:
        return None

    # remove variables that shall not be printed
    used_vars: set[Variable] = {v for v in stack_variables if not skip_variable(v)}

    # remove objs and attributes
    rem_obj_names = {v.name for v in used_vars if _skip_objs(v.name, v.value)}
    rem_objs = {v for v in used_vars for rem_name in rem_obj_names if v.name.startswith(rem_name)}
    used_vars -= rem_objs

    # attributes
    dotted_names: set[str] = {n.name.split('.')[0] for n in used_vars if '.' in n.name}

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
        # both name and value can be a multiline string
        # -> try to format it nicely

        name_lines = name.splitlines()
        for line in name_lines[:-1]:
            tb.append(f'{" " * (PRE_INDENT + 1):s}{line:s}')

        last_name_line = name_lines[-1]
        for nr, line in enumerate(repr(value).splitlines()):
            if not nr:
                tb.append(f'{" " * (PRE_INDENT + 1):s}{last_name_line:s} = {line}')
            else:
                tb.append(f'{" " * (PRE_INDENT + 1):s}{" " * len(last_name_line):s}   {line}')

    tb.append(SEPARATOR_VARIABLES)
