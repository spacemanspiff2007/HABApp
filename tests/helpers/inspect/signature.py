import inspect
from typing import Final

import pytest


def assert_same_signature(func_a, func_b, *, eval_str: bool = True,
                          check_docstring: bool = True, ignore_return: bool = False) -> bool:

    sig_a: inspect.Signature = inspect.signature(func_a, eval_str=eval_str)
    sig_b: inspect.Signature = inspect.signature(func_b, eval_str=eval_str)

    if ignore_return:
        sig_a = sig_a.replace(return_annotation=inspect.Signature.empty)
        sig_b = sig_b.replace(return_annotation=inspect.Signature.empty)

    assert sig_a == sig_b, f'\n  {sig_a}\n  {sig_b}\n'

    if check_docstring:
        doc_a: Final = inspect.getdoc(func_a)
        doc_b: Final = inspect.getdoc(func_b)
        assert doc_a == doc_b, f'\n  {doc_a}\n  {doc_b}\n'

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
