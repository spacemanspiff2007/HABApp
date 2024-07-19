import unittest
from datetime import timedelta

from pendulum import UTC
from pendulum import now as pd_now

from HABApp.core.items import Item

from . import ItemTests


class TestItem(ItemTests):
    CLS = Item
    TEST_VALUES = [0, 'str', (1, 2, 3)]
    TEST_CREATE_ITEM = {'initial_value': 0}


class TestCasesItem(unittest.TestCase):

    def test_repr(self):
        i = Item('test')
        self.assertGreater(len(str(i)), 23)

    def test_time_update(self):
        i = Item('test')
        i.set_value('test')
        i._last_change.set(pd_now(UTC) - timedelta(seconds=5), events=False)
        i._last_update.set(pd_now(UTC) - timedelta(seconds=5), events=False)
        i.set_value('test')

        self.assertGreater(i._last_update.dt, pd_now(UTC) - timedelta(milliseconds=100))
        self.assertLess(i._last_change.dt, pd_now(UTC) - timedelta(milliseconds=100))

    def test_time_change(self):
        i = Item('test')
        i.set_value('test')
        i._last_change.set(pd_now(UTC) - timedelta(seconds=5))
        i._last_update.set(pd_now(UTC) - timedelta(seconds=5))
        i.set_value('test1')

        self.assertGreater(i._last_update.dt, pd_now(UTC) - timedelta(milliseconds=100))
        self.assertGreater(i._last_change.dt, pd_now(UTC) - timedelta(milliseconds=100))


if __name__ == '__main__':
    unittest.main()
