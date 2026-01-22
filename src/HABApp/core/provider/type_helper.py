import ast
import inspect
import re
from collections.abc import AsyncGenerator, Generator
from enum import StrEnum
from importlib import import_module
from types import ModuleType
from typing import Annotated, Any, Final, get_args, get_origin


def _is_type_checking_condition(expr: ast.expr) -> bool:
    return isinstance(expr, ast.Name) and isinstance(expr.ctx, ast.Load) and expr.id == 'TYPE_CHECKING'


def _get_import_statements(module: ast.Module, *, only_names: tuple[str, ...]) -> list[ast.stmt]:
    statements = []
    for stmt in module.body:
        if isinstance(stmt, ast.If) and not stmt.orelse and _is_type_checking_condition(stmt.test):
            if not only_names:
                statements.extend(stmt.body)
            else:
                for body_obj in stmt.body:
                    if not isinstance(body_obj, ast.ImportFrom):
                        continue
                    for name_obj in body_obj.names:
                        name = name_obj.asname or name_obj.name
                        if name in only_names:
                            statements.append(body_obj)
                            break

    return statements


def import_type_checking_hints(module: ModuleType | str, only_names: tuple[str, ...] = ()) -> None:
    if isinstance(module, str):
        module = import_module(module)

    module_source: Final = inspect.getsource(module)
    statements: Final = _get_import_statements(ast.parse(module_source), only_names=only_names)

    code = compile(ast.Module(statements, type_ignores=[]), f'<import TYPE_CHECKING in {module}>', 'exec')

    namespace = {}
    exec(code, namespace)  # noqa: S102

    # copy imports into original module so we can evaluate the type hints
    for k, v in namespace.items():
        if not hasattr(module, k):
            setattr(module, k, v)


def __get_func(obj: Any) -> Any:
    if isinstance(obj, (classmethod, staticmethod)):
        return obj.__func__
    return obj


class FactoryType(StrEnum):
    COROUTINE = 'coroutine'
    CALLABLE = 'callable'
    SYNC_GENERATOR = 'sync_generator'
    ASYNC_GENERATOR = 'async_generator'


def get_factory_type(obj: Any) -> FactoryType:

    obj = __get_func(obj)

    if inspect.isasyncgenfunction(obj):
        return FactoryType.ASYNC_GENERATOR
    if inspect.isgeneratorfunction(obj):
        return FactoryType.SYNC_GENERATOR
    if inspect.iscoroutinefunction(obj):
        return FactoryType.COROUTINE
    if inspect.isfunction(obj) or inspect.ismethod(obj) or inspect.isclass(obj):
        return FactoryType.CALLABLE

    msg = f'Unsupported factory type: {obj}'
    raise TypeError(msg)


def get_obj_annotations(obj: Any) -> dict[str, type]:

    func = __get_func(obj)

    try:
        annotations = inspect.get_annotations(func, eval_str=True)
    except NameError:
        import_type_checking_hints(func.__module__)
        annotations = inspect.get_annotations(func, eval_str=True)

    annotations.pop('return', None)
    return {k: _resolve_origins(v) for k, v in annotations.items()}


def _resolve_origins(original_hint: type) -> type:
    hint = original_hint
    while (origin := get_origin(hint)) is not None:
        if origin is AsyncGenerator:
            (hint, _) = get_args(hint)
        elif origin is Generator:
            (hint, _, _) = get_args(hint)
        elif origin is Annotated:
            hint = get_args(hint)[0]
        elif origin is dict:
            _arg_k, _arg_v = get_args(hint)
            hint = dict[_resolve_origins(_arg_k), _resolve_origins(_arg_v)]
            break
        elif origin is list:
            (_arg_l, ) = get_args(hint)
            hint = list[_resolve_origins(_arg_l)]
            break
        elif origin is tuple:
            _args = tuple(_resolve_origins(h) for h in get_args(hint))
            hint = tuple[*_args]
            break
        else:
            msg = f'Unsupported type hint origin {origin} for {original_hint}'
            raise TypeError(msg)

    return hint


def _find_top_level_separator(hint: str) -> int:
    bracket_count = 0
    for i, char in enumerate(hint):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
        elif bracket_count == 0 and char in ',|':
            return i
    return -1


def _get_types_from_hint(original_hint: str) -> tuple[str, ...]:
    types: list[str] = []

    stack: list[str] = [original_hint]
    while stack:
        hint = stack.pop()

        # Type
        if m := re.search(r'^\s*(?P<type>\w+)\s*$', hint, re.IGNORECASE):
            if (_type := m.group('type')) not in types:
                types.append(_type)
            continue

        # hint with args: Type[Args]
        if m := re.search(r'^\s*(?P<type>\w+)\s*\[(?P<inner>.*)\]$', hint, re.IGNORECASE):
            if (_type := m.group('type')) not in types:
                types.append(_type)
            stack.append(m.group('inner').strip())
            continue

        # type, type or type | type
        if _find_top_level_separator(hint) != -1:
            _separated = []
            while (pos := _find_top_level_separator(hint)) != -1:
                _separated.append(hint[:pos].strip())
                hint = hint[pos + 1:].strip()
            _separated.append(hint)
            stack.extend(reversed(_separated))
            continue

        msg = f'Unsupported fragment "{hint:s}" from {original_hint:s}'
        raise ValueError(msg)

    return tuple(types)


def get_return_type(obj: Any) -> type:
    obj_signature = inspect.signature(__get_func(obj))
    return_annotation = obj_signature.return_annotation

    if not isinstance(return_annotation, str):
        return _resolve_origins(return_annotation)

    obj_module = import_module(obj.__module__)

    # check if we have types in the return annotation and explicitly try to import these
    if (_hint_type_names := _get_types_from_hint(return_annotation)) and len(_hint_type_names) > 1:
        import_type_checking_hints(obj_module, only_names=_hint_type_names)

    # Add class namespace to eval
    local_ns = {}
    if hasattr(obj, '__qualname__') and '.' in obj.__qualname__:
        class_name = obj.__qualname__.split('.')[-2]
        cls = obj_module.__dict__.get(class_name)
        if isinstance(cls, type):
            local_ns = vars(cls)

    # Evaluate annotation if it's a string
    obj = eval(return_annotation.strip("'"), obj_module.__dict__, local_ns)  # noqa: S307
    return _resolve_origins(obj)
