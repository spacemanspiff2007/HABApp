import asyncio
import sys
import unittest

from HABApp.rule import Rule
from ..rule_runner import SimpleRuleRunner
from HABApp.core.const import loop


class TestCases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.runner = SimpleRuleRunner()
        self.rule: Rule = None

    def setUp(self):

        self.runner.set_up()
        self.rule = Rule()

    def tearDown(self):
        self.runner.tear_down()
        self.rule = None

    def set_ret(self, p1):
        self.ret = p1

    def test_run_func(self):
        self.rule.execute_subprocess(
            self.set_ret, sys.executable, '-c', 'import datetime; print(datetime.datetime.now())', capture_output=True
        )

        loop.run_until_complete(asyncio.gather(asyncio.sleep(0.5)))
        self.assertEqual(self.ret.returncode, 0)
        self.assertTrue(self.ret.stdout.startswith('20'))

    def test_run_func_no_cap(self):
        self.rule.execute_subprocess(
            self.set_ret, sys.executable, '-c', 'import datetime; print(datetime.datetime.now())', capture_output=False
        )

        # Test this call from __main__ to create thread save process watchers
        if sys.platform != "win32":
            asyncio.get_child_watcher()

        loop.run_until_complete(asyncio.gather(asyncio.sleep(0.5)))
        self.assertEqual(self.ret.returncode, 0)
        self.assertEqual(self.ret.stdout, None)
        self.assertEqual(self.ret.stderr, None)


    def test_exception(self):
        self.rule.execute_subprocess(self.set_ret, 'asdfasdf', capture_output=False)

        loop.run_until_complete(asyncio.gather(asyncio.sleep(0.5)))
        self.assertEqual(self.ret.returncode, -1)

        self.assertTrue(isinstance(self.ret.stderr, str))
        self.assertNotEqual(self.ret.stderr, '')


if __name__ == '__main__':
    unittest.main()
