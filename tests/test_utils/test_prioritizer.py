import unittest

from HABApp.util import ValuePrioritizer


class TestCases(unittest.TestCase):

    def setUp(self) -> None:
        self.value = None

    def cb(self, value):
        self.value = value


    def test_same_prio(self):
        p = ValuePrioritizer(on_value_change=self.cb)
        a1 = p.get_create_value(0, '1234')
        a2 = p.get_create_value(0, '1234')
        a2.set_value(1)
        self.assertEqual(self.value, 1)
        a1.set_value(2)
        self.assertEqual(self.value, 2)
        return p

    def test_diff_prio(self):
        p = self.test_same_prio()
        self.assertEqual(self.value, 2)

        b = p.get_create_value(10, '1234')
        b.set_value('asdf')
        self.assertEqual(self.value, 'asdf')



if __name__ == '__main__':
    unittest.main()
