from HABApp.core.items import BaseValueItem


def test_numeric():
    a = BaseValueItem('asdf', 1)
    assert a + 10 == 11
    assert a - 10 == -9
    assert a * 20 == 20
    assert a / 5 == 0.2

