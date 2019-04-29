import unittest
from datetime import datetime, timedelta, time

from HABApp import Rule, Runtime


class TestRuleFile:
    def suggest_rule_name(self, asdf):
        return ''


__HABAPP__RUNTIME__ = Runtime()
__UNITTEST__ = True
__HABAPP__RULE_FILE__ = TestRuleFile()
__HABAPP__RULES = []


def clear():
    global __HABAPP__RUNTIME__, __HABAPP__RULE_FILE__
    __HABAPP__RULE_FILE__ = TestRuleFile()
    __HABAPP__RULES.clear()


class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rule: Rule = None

    def setUp(self):
        self.rule = Rule()

    def tearDown(self):
        self.rule._cleanup()
        self.rule = None
        clear()

    def test_run_reoccurring(self):
        r = self.rule
        test = [time(11, 30, 0), timedelta(seconds=30), None]
        for t in test:
            r.run_on_weekends(t, lambda x : x)
            r.run_on_workdays(t, lambda x : x)
            r.run_on_every_day(t, lambda x : x)

            r.run_every(t, 60, lambda x : x)
            r.run_every(t, timedelta(seconds=30), lambda x : x)

        with self.assertRaises(AssertionError):
            r.run_on_weekends(datetime.now(), lambda x : x)
        with self.assertRaises(AssertionError):
            r.run_on_workdays(datetime.now(), lambda x : x)
        with self.assertRaises(AssertionError):
            r.run_on_every_day(datetime.now(), lambda x : x)
        with self.assertRaises(AssertionError):
            r.run_every(datetime.now(), 30, lambda x : x)

    def test_run_convenience_funcs(self):
        r = self.rule

        def cb():
            pass

        r.run_daily(cb)
        r.run_hourly(cb)
        r.run_minutely(cb)
        r.run_soon(cb)

    def test_run_scheduler(self):
        r = self.rule

        def cb():
            pass

        r.run_in(5, cb)

        for t in [time(11, 30, 0), timedelta(seconds=30), None, datetime.now() + timedelta(seconds=1)]:
            r.run_at(t, cb)


if __name__ == '__main__':
    unittest.main()
