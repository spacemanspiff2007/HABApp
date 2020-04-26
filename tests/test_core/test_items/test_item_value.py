from math import ceil, floor

from HABApp.core.items import BaseValueItem


def test_numeric():
    a = BaseValueItem('asdf', 1)
    b = BaseValueItem('asdf', 5)

    assert a + 10 == 11
    assert a - 10 == -9
    assert a * 20 == 20
    assert a / 5 == 0.2

    assert a + b == 6
    assert a - b == -4


def test_built_in():
    a = BaseValueItem('asdf', 1.49)
    assert round(a, 1) == 1.5
    assert round(a) == 1

    assert floor(a) == 1
    assert ceil(a) == 2


def test_unary():
    a = BaseValueItem('asdf', -1)
    assert abs(a) == 1
    assert -a == 1


def test_cast():
    assert float(BaseValueItem('asdf', 1)) == 1.0
    assert int(BaseValueItem('asdf', 1.5)) == 1
