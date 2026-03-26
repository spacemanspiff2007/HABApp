from math import ceil, floor

from HABApp.core.items import BaseValueItem


def _get_item(value: float) -> BaseValueItem:
    return BaseValueItem('asdf', value, event_bus=None)


def test_numeric() -> None:
    a = _get_item(1)
    b = _get_item(5)

    assert a + 10 == 11
    assert a - 10 == -9
    assert a * 20 == 20
    assert a / 5 == 0.2

    assert a + b == 6
    assert a - b == -4


def test_built_in() -> None:
    a = _get_item(1.49)
    assert round(a, 1) == 1.5
    assert round(a) == 1

    assert floor(a) == 1
    assert ceil(a) == 2


def test_unary() -> None:
    a = _get_item(-1)
    assert abs(a) == 1
    assert -a == 1


def test_cast() -> None:
    assert float(_get_item(1)) == 1.0
    assert int(_get_item(1.5)) == 1


def test_compare() -> None:
    a = _get_item(1)
    assert a < 2
    assert a <= 2
    assert a > 0
    assert a >= 0

    assert a == 1
    assert a != 4
