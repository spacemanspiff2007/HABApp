import unittest

from HABApp.core.items import ColorItem


class TestCasesItem(unittest.TestCase):

    def test_repr(self):
        str(ColorItem('test'))

    def test_set_func(self):
        i = ColorItem('test')
        self.assertEqual(i.hue, 0)
        self.assertEqual(i.saturation, 0)
        self.assertEqual(i.value, 0)

        i.set_state(30, 50, 70)

        self.assertEqual(i.hue, 30)
        self.assertEqual(i.saturation, 50)
        self.assertEqual(i.value, 70)

        self.assertEqual(i.state, (30, 50, 70))

    def test_set_func_touple(self):
        i = ColorItem('test')
        self.assertEqual(i.hue, 0)
        self.assertEqual(i.saturation, 0)
        self.assertEqual(i.value, 0)

        i.set_state((22, 33.3, 77), None)

        self.assertEqual(i.hue, 22)
        self.assertEqual(i.saturation, 33.3)
        self.assertEqual(i.value, 77)

        self.assertEqual(i.state, (22, 33.3, 77))

    def test_rgb_to_hsv(self):
        i = ColorItem('test')
        i.set_rgb(193, 25, 99)

        self.assertEqual(int(i.hue), 333)
        self.assertEqual(int(i.saturation), 87)
        self.assertEqual(int(i.value), 75)

    def test_hsv_to_rgb(self):
        i = ColorItem('test', 23, 44, 66)
        self.assertEqual(i.get_rgb(), (168, 122, 94))



if __name__ == '__main__':
    unittest.main()
