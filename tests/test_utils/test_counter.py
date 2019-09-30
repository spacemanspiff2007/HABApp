from HABApp.util import CounterItem

from ..test_core import ItemTests


class TestCounterItem(ItemTests):
    CLS = CounterItem
    TEST_VALUES = [5, -10, 10]
    TEST_CREATE_ITEM = {'initial_value': 10}


def test_reset():
    c = CounterItem('TestItem', initial_value=10)
    c.increase()
    assert c.value == 11
    c.reset()
    assert c.value == 10
