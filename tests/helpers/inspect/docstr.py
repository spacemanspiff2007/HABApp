import importlib
import inspect
import re
from typing import Any, Optional

import pytest


RE_IVAR = re.compile(r':ivar\s+([^:]+?)\s+(\w+)\s*:', re.IGNORECASE)


class IVarRedefinitionError(Exception):
    pass


class ExpectedHintNotFoundError(Exception):
    pass


def get_ivars_from_docstring(cls_obj: type[object], correct_hints: dict[str, Any] | None = None) -> dict[str, Any]:
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
                    msg = f'Redefinition of type hint for {cls.__name__}.{name}: {ret[name]} != {hint}'
                    raise IVarRedefinitionError(msg)
                ret[name] = hint

    # check that we have found the specified hint
    for name, correct_hint in correct_hints.items():
        if name not in ret:
            msg = f'Expected hint not found for {cls_obj.__name__}.{name}: {correct_hint}'
            raise ExpectedHintNotFoundError(msg)

    return ret


def test_ivar_redefinition() -> None:
    class Parent:
        """:ivar str a:"""

    class Child(Parent):
        """:ivar Optional[dict[str, str]] a:"""

    with pytest.raises(IVarRedefinitionError) as e:
        get_ivars_from_docstring(Child)
    assert str(e.value) == "Redefinition of type hint for Parent.a: " \
                           "typing.Optional[typing.dict[str, str]] != <class 'str'>"

    with pytest.raises(ExpectedHintNotFoundError) as e:
        get_ivars_from_docstring(Child, {'a': dict[str, str]})
    assert str(e.value) == 'Expected hint not found for Child.a: typing.dict[str, str]'

    get_ivars_from_docstring(Child, {'a': Optional[dict[str, str]]})
