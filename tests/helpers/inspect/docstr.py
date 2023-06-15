import importlib
import inspect
import re
from typing import Any, Type, Dict, Optional

import pytest

RE_IVAR = re.compile(r':ivar\s+([^:]+?)\s+(\w+)\s*:', re.IGNORECASE)


class IVarRedefinitionError(Exception):
    pass


class ExpectedHintNotFound(Exception):
    pass


def get_ivars_from_docstring(cls_obj: Type[object], correct_hints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if correct_hints is None:
        correct_hints = {}

    ret = {}
    for cls in inspect.getmro(cls_obj):
        mod = importlib.import_module(cls.__module__)
        docstr = cls.__doc__
        if not docstr:
            continue

        for hint, name in RE_IVAR.findall(docstr):
            try:
                hint = eval(hint, mod.__dict__)
            except Exception:
                print(f'Error while evaluating "{hint}" of {cls.__name__}')
                raise

            if (correct_hint := correct_hints.get(name)) is not None:
                # only save the correct one
                if hint == correct_hint:
                    ret[name] = hint
            else:
                if name in ret and ret[name] != hint:
                    raise IVarRedefinitionError(
                        f'Redefinition of type hint for {cls.__name__}.{name}: {ret[name]} != {hint}'
                    )
                ret[name] = hint

    # check that we have found the specified hint
    for name, correct_hint in correct_hints.items():
        if name not in ret:
            raise ExpectedHintNotFound(f'Expected hint not found for {cls_obj.__name__}.{name}: {correct_hint}')

    return ret


def test_ivar_redefinition():
    class Parent:
        """:ivar str a:"""

    class Child(Parent):
        """:ivar Optional[Dict[str, str]] a:"""

    with pytest.raises(IVarRedefinitionError) as e:
        get_ivars_from_docstring(Child)
    assert str(e.value) == "Redefinition of type hint for Parent.a: " \
                           "typing.Optional[typing.Dict[str, str]] != <class 'str'>"

    with pytest.raises(ExpectedHintNotFound) as e:
        get_ivars_from_docstring(Child, {'a': Dict[str, str]})
    assert str(e.value) == "Expected hint not found for Child.a: typing.Dict[str, str]"

    get_ivars_from_docstring(Child, {'a': Optional[Dict[str, str]]})
