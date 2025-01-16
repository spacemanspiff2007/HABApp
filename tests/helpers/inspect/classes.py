import inspect
from collections.abc import Iterable
from typing import Any, get_type_hints

import pytest

from .docstr import get_ivars_from_docstring


def check_class_annotations(cls: type[object],
                            correct_hints: dict[str, Any] | None = None,
                            init_alias: dict[str, str] | None = None, init_missing: Iterable[str] = (),
                            *, annotations_missing=False, ignore: Iterable[str] = ()) -> dict[str, Any]:
    """Ensure that the annotations match with the actual variables"""

    if correct_hints is None:
        correct_hints = {}

    name = cls.__name__

    annotation_vars = get_type_hints(cls)
    # ignore the specified annotations
    for _name in ignore:
        annotation_vars.pop(_name, None)

    docstr_vars = get_ivars_from_docstring(cls, correct_hints)
    init_vars = inspect.getfullargspec(cls).annotations

    # If we return None we can just skip the annotation because it's most likely to be auto gernerated
    if 'return' not in annotation_vars and 'return' in init_vars and init_vars['return'] is None:
        del init_vars['return']

    # if we don't have annotations we can use the docstr vars
    if annotations_missing:
        assert not annotation_vars
        annotation_vars = docstr_vars.copy()

    if init_alias is not None:
        for _alias, _name in init_alias.items():
            if _alias in init_vars:
                assert _name not in init_vars
                init_vars[_name] = init_vars.pop(_alias)

    # if it's missing from init we just copy and paste it
    for var_name in init_missing:
        assert var_name not in init_vars
        for _hint_src in annotation_vars, docstr_vars:
            if var_hint := _hint_src.get(var_name):
                init_vars[var_name] = var_hint
                break

    # ensure that we have the same set of variables
    if not (set(docstr_vars) == set(init_vars) == set(annotation_vars)):
        print(f'\nDocs invalid for: {name}')
        print(f'Docstr    : {", ".join(sorted(docstr_vars))}')
        print(f'Annotation: {", ".join(sorted(annotation_vars))}')
        print(f'__init__  : {", ".join(sorted(init_vars))}')
        pytest.fail(f'Docs invalid for: {name}')

    # ensure that both annotation and docstr have the same type
    assert docstr_vars == annotation_vars, f'\n{name}\n{docstr_vars}\n{annotation_vars}'

    # Check that the instance vars match with the annotation
    for var_name, var_value in init_vars.items():
        annotation = annotation_vars[var_name]

        # We don't check Any, e.g. in the base class
        if var_value is Any:
            continue

        if var_value != annotation:
            pytest.fail(
                f'Constructor of {name} does not match type hint for {var_name}: '
                f'{var_value} != {annotation}'
            )

    return annotation_vars or docstr_vars
