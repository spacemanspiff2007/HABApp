from HABApp.core.const import MISSING
from HABApp.core.lib.funcs import compare


def test_compare_single() -> None:
    assert compare(1, eq=1)
    assert compare(1, equal=1)

    assert compare(1, le=1)
    assert compare(1, lower_equal=1)
    assert compare(1, le=2)
    assert compare(1, lower_equal=2)

    assert compare(1, lt=2)
    assert compare(1, lower_than=2)
    assert not compare(1, lt=1)
    assert not compare(1, lower_than=1)

    assert compare(1, gt=0)
    assert compare(1, greater_than=0)
    assert not compare(1, gt=1)
    assert not compare(1, greater_than=1)

    assert compare(1, ge=0)
    assert compare(1, greater_equal=0)
    assert compare(1, ge=1)
    assert compare(1, greater_equal=1)

    assert compare(None, is_=None)
    assert not compare(None, is_=True)

    assert compare(None, is_not=True)
    assert not compare(None, is_not=None)


def test_compare_multi() -> None:
    assert compare(5, le=5, ge=7)
    assert compare(7, le=5, ge=7)
    assert not compare(6, le=5, ge=7)


def test_compare_missing() -> None:
    assert compare(5, le=5, ge=MISSING)
    assert not compare(7, le=5, ge=MISSING)
