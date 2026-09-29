import inspect
import re
from collections.abc import Sequence
from inspect import Parameter

import pytest


def _drop_parameter(sig: inspect.Signature, p: Parameter) -> inspect.Signature:
    if p.name not in sig.parameters:
        return sig

    existing = sig.parameters[p.name]
    assert existing == p, f'Parameters do not match:\n  {existing}\n  {p}'

    params = [param for name, param in sig.parameters.items() if name != p.name]
    return sig.replace(parameters=params)


def _drop_parameter_from_docstr(docs: str, p: Parameter) -> str:
    if not docs:
        return docs

    return re.sub(r'^\s*:param\s+' + p.name + r':\s+[^\n]+\n', '', docs, flags=re.MULTILINE)


def assert_same_signature(func_a, func_b, *, eval_str: bool = True,
                          check_docstring: bool = True, ignore_return: bool = False,
                          drop_params: Sequence[Parameter] | None = None) -> bool:

    sig_a: inspect.Signature = inspect.signature(func_a, eval_str=eval_str)
    sig_b: inspect.Signature = inspect.signature(func_b, eval_str=eval_str)

    if ignore_return:
        sig_a = sig_a.replace(return_annotation=inspect.Signature.empty)
        sig_b = sig_b.replace(return_annotation=inspect.Signature.empty)

    if drop_params:
        for p in drop_params:
            sig_a = _drop_parameter(sig_a, p)
            sig_b = _drop_parameter(sig_b, p)

    assert sig_a == sig_b, f'\n  {sig_a}\n  {sig_b}\n'

    if check_docstring:
        doc_a: str = inspect.getdoc(func_a) or ''
        doc_b: str = inspect.getdoc(func_b) or ''

        if drop_params:
            for p in drop_params:
                doc_a = _drop_parameter_from_docstr(doc_a, p)
                doc_b = _drop_parameter_from_docstr(doc_b, p)

        assert doc_a == doc_b, f'\n  {doc_a.replace('\n', '\\n')}\n  {doc_b.replace('\n', '\\n')}\n'

    return True


def test_assert_same_signature() -> None:
    def func1(a: int, b: str | None = None) -> float:
        """Doc1"""

    def func1_no_ret(a: int, b: str | None = None) -> None:
        """Doc1"""

    def func1_diff_args(a: int, b: str = None) -> float:  # noqa: RUF013
        """Doc1"""

    def func1_diff_doc(a: int, b: str | None = None) -> float:
        """Doc2"""

    with pytest.raises(AssertionError):
        assert_same_signature(func1, func1_no_ret)

    with pytest.raises(AssertionError):
        assert_same_signature(func1, func1_diff_args)

    with pytest.raises(AssertionError):
        assert_same_signature(func1, func1_diff_doc)
