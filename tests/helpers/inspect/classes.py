import importlib
import inspect
import re
from typing import Iterable, Optional, get_origin, Union, get_args, Any, Type, get_type_hints

import pytest

from tests.helpers.inspect.module import get_module_classes

RE_IVAR = re.compile(r':ivar\s+([^:]+?)\s+(\w+)\s*:', re.IGNORECASE)


def get_ivars_from_docstring(cls: Type[object]) -> dict[str, Any]:
    ret = {}
    for cls in inspect.getmro(cls):
        mod = importlib.import_module(cls.__module__)
        docstr = cls.__doc__
        if not docstr:
            continue

        for hint, name in RE_IVAR.findall(docstr):
            hint = eval(hint, mod.__dict__)
            if name in ret and ret[name] != hint:
                pytest.fail(f'Redefinition of type hint for {cls}.{name}! {ret[name]} != {hint}')
            ret[name] = hint
    return ret


def check_class_annotations(module_name: str, exclude: Optional[Iterable[str]] = None):
    """Ensure that the annotations match with the actual variables"""

    classes = get_module_classes(module_name, exclude=exclude)
    for name, cls in classes.items():
        annotation_vars = get_type_hints(cls)
        docstr_vars = get_ivars_from_docstring(cls)

        c = cls()
        instance_vars = dict(filter(
            lambda x: not x[0].startswith('__'),
            dict(inspect.getmembers(c, lambda x: not inspect.ismethod(x))).items())
        )

        # ensure that we have the same set of variables
        if not (set(docstr_vars) == set(instance_vars) == set(annotation_vars)):
            print(f'\nDocs invalid for: {name}')
            print(f'Docstr    : {", ".join(sorted(docstr_vars))}')
            print(f'Annotation: {", ".join(sorted(annotation_vars))}')
            print(f'Instance  : {", ".join(sorted(instance_vars))}')
            pytest.fail(f'Docs invalid for: {name}')

        # ensure that both annotation and docstr have the same type
        assert docstr_vars == annotation_vars, f'\n{name}\n{docstr_vars}\n{annotation_vars}'

        # Check that the instance vars match with the annotation
        for var_name, var_value in instance_vars.items():
            annotation = annotation_vars[var_name]

            # We don't check Any
            if annotation is Any:
                continue

            annotation_origin = get_origin(annotation)
            annotation_args = get_args(annotation)

            def assert_type(obj, target_type):
                assert isinstance(obj, target_type), f'{name}.{var_name}: {type(obj)} != {target_type}'

            # get_origin returns None for unsupported types, e.g. if we have str
            if annotation_origin is None:
                assert not annotation_args
                assert_type(var_value, annotation)
            elif annotation_origin is Union:
                assert annotation_args
                assert isinstance(var_value, annotation_args)
            elif annotation_origin in (type_test := (set, frozenset, list, tuple)):
                assert_type(var_value, type_test)
                for child in var_value:
                    assert isinstance(child, annotation_args)
            elif annotation_origin in (type_test := (dict, )):
                assert_type(var_value, type_test)
                type_key, type_value = annotation_args
                for key, value in var_value.items():
                    if type_key is not Any:
                        assert isinstance(key, type_key)
                    if type_value is not Any:
                        assert isinstance(value, type_value)
            else:
                raise ValueError(f'Unsupported: {annotation_origin} for {name}')
