import unittest

from HABApp.util import PrioritizedValue


class TestCases(unittest.TestCase):

    def setUp(self) -> None:
        self.value = None

    def cb(self, value):
        self.value = value

    def test_1(self):
        p = PrioritizedValue(on_change=self.cb)
        c = p.add_value(0, '1234')
        self.assertEqual(c._value, '1234')

    def test_same_prio(self):
        p = PrioritizedValue(on_change=self.cb)
        a1 = p.add_value(0, '1234')
        a2 = p.add_value(0, '1234')
        a2.set_value(1)
        self.assertEqual(self.value, 1)
        a1.set_value(2)
        self.assertEqual(self.value, 2)
        return p

    def test_diff_prio(self):
        p = self.test_same_prio()
        self.assertEqual(self.value, 2)
        
        a = p.add_value(0, '1234')
        a.set_enabled(True)
        self.assertEqual(self.value, '1234')

        b = p.add_value(10, '1234')
        b.set_value('asdf')
        self.assertEqual(self.value, 'asdf')

        a.set_value(4444)
        self.assertEqual(self.value, 'asdf')


if __name__ == '__main__':
    unittest.main()
