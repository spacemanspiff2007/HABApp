import inspect
from collections.abc import Iterable
from typing import Any, Final, get_type_hints

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

    annotation_vars: Final = get_type_hints(cls)
    docstr_vars: Final = get_ivars_from_docstring(cls, correct_hints)
    init_vars: Final = inspect.getfullargspec(cls).annotations

    for _obj in (annotation_vars, docstr_vars, init_vars):
        for _name in ignore:
            _obj.pop(_name, None)

    # If we return None we can just skip the annotation because it's most likely to be auto generated
    if 'return' not in annotation_vars and 'return' in init_vars and init_vars['return'] is None:
        del init_vars['return']

    # if we don't have annotations we can use the docstr vars
    if annotations_missing:
        # check that the docstr vars match the correct hints
        for _annotation_name, _annotation_type in annotation_vars.items():
            assert docstr_vars[_annotation_name] == _annotation_type

        # since the annotation vars are a subset we overwrite the annotation vars
        annotation_vars = docstr_vars.copy()

    if init_alias is not None:
        for _alias, _name in init_alias.items():
            if _alias in init_vars:
                assert _name not in init_vars
                init_vars[_name] = init_vars.pop(_alias)

    # if it's missing from init we just copy and paste it
    for var_name in init_missing:
        assert var_name not in init_vars, f'{var_name} is in {init_vars}'
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
