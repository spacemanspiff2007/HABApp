import unittest
from datetime import datetime, timedelta

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
        i.last_change = datetime.now() - timedelta(seconds=5)
        i.last_update = datetime.now() - timedelta(seconds=5)
        i.set_value('test')

        self.assertGreater(i.last_update, datetime.now() - timedelta(milliseconds=100))
        self.assertLess(i.last_change, datetime.now() - timedelta(milliseconds=100))

    def test_time_change(self):
        i = Item('test')
        i.set_value('test')
        i.last_change = datetime.now() - timedelta(seconds=5)
        i.last_update = datetime.now() - timedelta(seconds=5)
        i.set_value('test1')

        self.assertGreater(i.last_update, datetime.now() - timedelta(milliseconds=100))
        self.assertGreater(i.last_change, datetime.now() - timedelta(milliseconds=100))


if __name__ == '__main__':
    unittest.main()
