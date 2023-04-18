import inspect
from typing import Optional

import pytest


def assert_same_signature(func_a, func_b):
    sig_a = inspect.signature(func_a)
    sig_b = inspect.signature(func_b)
    assert sig_a == sig_b, f'\n  {sig_a}\n  {sig_b}\n'

    doc_a = inspect.getdoc(func_a)
    doc_b = inspect.getdoc(func_b)
    assert doc_a == doc_b

    return True


def test_assert_same_signature():
    def func1(a: int, b: Optional[str] = None) -> float:
        """Doc1"""

    def func1_no_ret(a: int, b: Optional[str] = None):
        """Doc1"""

    def func1_diff_args(a: int, b: str = None) -> float:
        """Doc1"""

    def func1_diff_doc(a: int, b: Optional[str] = None) -> float:
        """Doc2"""

    with pytest.raises(AssertionError):
        assert_same_signature(func1, func1_no_ret)

    with pytest.raises(AssertionError):
        assert_same_signature(func1, func1_diff_args)

    with pytest.raises(AssertionError):
        assert_same_signature(func1, func1_diff_doc)
