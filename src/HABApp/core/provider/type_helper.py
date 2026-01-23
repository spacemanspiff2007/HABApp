import ast
import inspect
import re
from collections.abc import AsyncGenerator, Generator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from enum import StrEnum
from importlib import import_module
from inspect import isclass
from types import ModuleType
from typing import Any, Final, get_args, get_origin


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
    SYNC_CONTEXT_MANAGER = 'sync_context_manager'
    ASYNC_CONTEXT_MANAGER = 'async_context_manager'


def get_factory_type(obj: Any) -> FactoryType:

    obj = __get_func(obj)

    if inspect.isasyncgenfunction(obj):
        return FactoryType.ASYNC_GENERATOR

    if inspect.isgeneratorfunction(obj):
        return FactoryType.SYNC_GENERATOR

    if inspect.iscoroutinefunction(obj):
        return FactoryType.COROUTINE

    if inspect.isclass(obj):
        if issubclass(obj, AbstractAsyncContextManager) or (hasattr(obj, '__aenter__') and hasattr(obj, '__aexit__')):
            return FactoryType.ASYNC_CONTEXT_MANAGER
        if issubclass(obj, AbstractContextManager) or (hasattr(obj, '__enter__') and hasattr(obj, '__exit__')):
            return FactoryType.SYNC_CONTEXT_MANAGER
        return FactoryType.CALLABLE

    if inspect.isfunction(obj) or inspect.ismethod(obj):
        return FactoryType.CALLABLE

    msg = f'Unsupported factory type: {obj}'
    raise TypeError(msg)


def get_obj_parameters(obj: Any) -> dict[str, type]:

    func = __get_func(obj)
    obj_signature = inspect.signature(func)
    if not obj_signature.parameters:
        return {}

    try:
        annotations = inspect.get_annotations(func, eval_str=True)
    except NameError:

        # identify hints which caused this error
        params_annotations: set[str] = set()
        for param in obj_signature.parameters.values():
            params_annotations.update(_get_types_from_hint(param.annotation))

        # Explicitly try to import these types
        try:
            import_type_checking_hints(func.__module__, only_names=tuple(params_annotations))
        except KeyError:
            msg = f'Error while importing! Did you use a relative import? Tried {", ".join(sorted(params_annotations))}'
            # keep the original exception!
            raise RuntimeError(msg)  # noqa: B904

        # try again
        annotations = inspect.get_annotations(func, eval_str=True)

    annotations.pop('return', None)
    return {k: _resolve_origins(v) for k, v in annotations.items()}


def _resolve_origins(hint: type) -> type:
    if (origin := get_origin(hint)) is None:
        return hint

    if origin is AsyncGenerator:
        (hint, _) = get_args(hint)
    elif origin is Generator:
        (hint, _, _) = get_args(hint)
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
    if isclass(obj):
        return obj

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
