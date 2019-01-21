import unittest

from HABApp.util import Threshold


class TestCases(unittest.TestCase):

    def test_constructor(self):
        t = Threshold(10, 20)
        self.assertEqual(t.current_threshold, 20)
        t = Threshold(20, 10)
        self.assertEqual(t.current_threshold, 20)

    def test_a(self):
        t = Threshold(10, 20)

        self.assertFalse( 19 > t)
        # Über obere Grenze
        self.assertTrue(21 > t)
        self.assertTrue(20 > t)
        self.assertTrue(11 > t)

        # unter untere Grenze
        self.assertFalse(9 > t)
        self.assertFalse(19 > t)

    def test_b(self):
        t = Threshold(10, 20)
        self.assertEqual(t.current_threshold, 20)

        self.assertFalse(19 >= t)
        # Über obere Grenze
        self.assertTrue(21 >= t)
        self.assertTrue(10 >= t)

        # unter untere Grenze
        self.assertFalse(9 >= t)
        self.assertFalse(19 >= t)


if __name__ == '__main__':
    unittest.main()
