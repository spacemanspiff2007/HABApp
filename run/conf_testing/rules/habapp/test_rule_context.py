from time import sleep

from HABApp import Rule
from HABApp.core.internals import get_current_context
from HABAppTests import TestBaseRule


class OtherRule(Rule):

    def check_context(self):
        assert get_current_context() is self._habapp_ctx


other_rule = OtherRule()


def func_no_context(target_context):
    assert get_current_context() is target_context


class TestContext(TestBaseRule):

    def __init__(self):
        super().__init__()
        self.add_test('TestGetContext', self.test_get_context)
        self.add_test('TestSchedulerContext', self.test_scheduler_context)

    def test_get_context(self):
        assert get_current_context() is self._habapp_ctx
        other_rule.check_context()

    def test_scheduler_context(self):
        self.run.soon(func_no_context, self._habapp_ctx)
        self.run.soon(other_rule.check_context)
        sleep(0.1)


TestContext()
