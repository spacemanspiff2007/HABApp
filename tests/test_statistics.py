import unittest

from HABApp.classes import Statistics


class TestCases(unittest.TestCase):

    def test_constructor(self):
        with self.assertRaises(ValueError):
            Statistics()
        Statistics(max_age=20)
        Statistics(max_samples=20)

    def test_basic(self):
        stat = Statistics(max_age=20)
        stat.add_value(1)
        stat.add_value(2)
        stat.add_value(3)
        self.assertEqual(stat.last_value, 3)
        self.assertEqual(stat.min, 1)
        self.assertEqual(stat.max, 3)
        self.assertEqual(stat.mean, 2)
        self.assertEqual(stat.median, 2)

        stat.add_value(0)
        self.assertEqual(stat.median, 1.5)


if __name__ == '__main__':
    unittest.main()
