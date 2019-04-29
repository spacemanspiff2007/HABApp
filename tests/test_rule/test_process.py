import asyncio
import sys
import unittest

import HABApp
from HABApp.rule import Rule

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())




class TestRuleFile:
    def suggest_rule_name(self, asdf):
        return ''

__HABAPP__RUNTIME__ = HABApp.Runtime()
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
        self.ret = None

    def setUp(self):
        self.rule = Rule()
        self.ret = None

    def tearDown(self):
        self.rule._cleanup()
        self.rule = None
        clear()

    def set_ret(self, p1):
        self.ret = p1

    def test_run_func(self):
        self.rule.execute_subprocess(
            self.set_ret, sys.executable, '-c', 'import datetime; print(datetime.datetime.now())', capture_output=True
        )

        asyncio.get_child_watcher()
        asyncio.get_event_loop().run_until_complete(asyncio.gather(asyncio.sleep(0.5)))
        self.assertEqual(self.ret.returncode, 0)
        self.assertTrue(self.ret.stdout.startswith('20'))

    def test_exception(self):
        self.rule.execute_subprocess(self.set_ret, 'asdfasdf', capture_output=False)

        asyncio.get_event_loop().run_until_complete(asyncio.gather(asyncio.sleep(0.5)))
        self.assertEqual(self.ret.returncode, -1)

        self.assertTrue(isinstance(self.ret.stderr, str))
        self.assertNotEqual(self.ret.stderr, '')


if __name__ == '__main__':
    unittest.main()
