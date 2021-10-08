import time

from HABAppTests.test_rule._rest_patcher import RestPatcher
from HABAppTests.test_rule.test_case import TestResult, TestResultStatus


class TestCase:
    def __init__(self, name: str, func: callable, args=[], kwargs={}):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self, res: TestResult) -> TestResult:
        time.sleep(0.05)

        try:
            with RestPatcher(f'{res.cls_name}.{res.test_name}'):
                ret = self.func(*self.args, **self.kwargs)
                if ret:
                    res.set_state(TestResultStatus.FAILED)
                    res.add_msg(f'{ret}')
                else:
                    res.set_state(TestResultStatus.PASSED)
        except Exception as e:
            res.exception(e)

        time.sleep(0.05)
        return res
