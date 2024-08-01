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

        self.assertFalse( t < 19)
        # Über obere Grenze
        self.assertTrue(t < 21)
        self.assertTrue(t < 20)
        self.assertTrue(t < 11)

        # unter untere Grenze
        self.assertFalse(t < 9)
        self.assertFalse(t < 19)

    def test_b(self):
        t = Threshold(10, 20)
        self.assertEqual(t.current_threshold, 20)

        self.assertFalse(t <= 19)
        # Über obere Grenze
        self.assertTrue(t <= 21)
        self.assertTrue(t <= 10)

        # unter untere Grenze
        self.assertFalse(t <= 9)
        self.assertFalse(t <= 19)


if __name__ == '__main__':
    unittest.main()
