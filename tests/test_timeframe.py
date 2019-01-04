import unittest, datetime, time

import HABApp.util.timeframe
from HABApp.util import TimeFrame

def get_date( name, h, m, s = 0):
    __date = {
        "mo": (2019, 1, 7),
        "di": (2019, 1, 1),
        "mi": (2019, 1, 2),
        "do": (2019, 1, 3),
        "fr": (2019, 1, 4),
        "sa": (2019, 1, 5),
        "so": (2019, 1, 6),
    }
    
    return datetime.datetime(*__date[name], h, m, s)
    

class Basic(unittest.TestCase):

    def setUp(self):
        self.all_days = ['mo', 'di', 'mi', 'do', 'fr', 'sa', 'so']

    def test_single_days(self):
        for day_test in self.all_days:
            t = TimeFrame(f'{day_test},8:30:00-9:31')
            # boundary checks inside
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(day_test, 8, 30, 1)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(day_test, 9, 30, 59)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(day_test, 8, 31)
            self.assertEqual(t.is_now(), True)

            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(day_test, 8, 29, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(day_test, 9, 32)
            self.assertEqual(t.is_now(), False)

            days = self.all_days.copy()
            days.remove(day_test)
            for d in days:
                HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 31)
                self.assertEqual(t.is_now(), False)

    def test_all_days(self):
        t = TimeFrame(f'8:30:00-9:31')
        for d in self.all_days:
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 30, 1)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 30, 59)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 31)
            self.assertEqual(t.is_now(), True)

            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 29, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 32)
            self.assertEqual(t.is_now(), False)


    def test_weekdays(self):
        t = TimeFrame('weekdays,8:30:00-9:31:00')

        self.all_days.remove('sa')
        self.all_days.remove('so')

        for d in ['sa', 'so']:
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 30, 1)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 30, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 31)
            self.assertEqual(t.is_now(), False)

            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 29, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 32)
            self.assertEqual(t.is_now(), False)

        for d in self.all_days:
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 30, 1)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 30, 59)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 31)
            self.assertEqual(t.is_now(), True)

            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 29, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 32)
            self.assertEqual(t.is_now(), False)

    def test_weekends(self):
        t = TimeFrame('weekends,8:30:00-9:31:00')
        self.all_days.remove('sa')
        self.all_days.remove('so')

        for d in ['sa', 'so']:
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 30, 1)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 30, 59)
            self.assertEqual(t.is_now(), True)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 31)
            self.assertEqual(t.is_now(), True)

            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 29, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 32)
            self.assertEqual(t.is_now(), False)

        for d in self.all_days:
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 30, 1)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 30, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 31)
            self.assertEqual(t.is_now(), False)

            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 8, 29, 59)
            self.assertEqual(t.is_now(), False)
            HABApp.util.timeframe._TIME_FUNC = lambda: get_date(d, 9, 32)
            self.assertEqual(t.is_now(), False)
        


    def test_invalid_day(self):
        self.assertRaises(ValueError, lambda: TimeFrame('asdf,8:30:00-9:30:00'))

    def test_invalid_hour(self):
        self.assertRaises(ValueError, lambda: TimeFrame('25:30:00-9:30:00'))
        
    def test_invalid_min(self):
        self.assertRaises(ValueError, lambda: TimeFrame('13:60:00'))
        
    def test_invalid_sec1(self):
        self.assertRaises(ValueError, lambda: TimeFrame('13:59:60'))
        
    def test_invalid_sec2(self):
        self.assertRaises(ValueError, lambda: TimeFrame('13:59:59-13:59:59'))


if __name__ == '__main__':
    unittest.main()
