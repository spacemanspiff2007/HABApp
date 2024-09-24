from time import sleep

from HABAppTests import TestBaseRule

from HABApp import Rule
from HABApp.core.internals import get_current_context


class OtherRule(Rule):

    def check_context(self) -> None:
        assert get_current_context() is self._habapp_ctx

    def async_check_context(self) -> None:
        assert get_current_context() is self._habapp_ctx


other_rule = OtherRule()


def func_no_context(target_context) -> None:
    assert get_current_context() is target_context


async def async_func_no_context(target_context) -> None:
    assert get_current_context() is target_context


class TestContext(TestBaseRule):

    def __init__(self) -> None:
        super().__init__()
        self.add_test('TestGetContext', self.test_get_context)
        self.add_test('TestSchedulerContext', self.test_scheduler_context)
        self.add_test('TestSchedulerAsyncContext', self.test_scheduler_async_context)

    def test_get_context(self) -> None:
        assert get_current_context() is self._habapp_ctx
        other_rule.check_context()

    def test_scheduler_context(self) -> None:
        self.run.soon(func_no_context, self._habapp_ctx)
        self.run.soon(other_rule.check_context)
        sleep(0.1)

    def test_scheduler_async_context(self) -> None:
        self.run.soon(async_func_no_context, self._habapp_ctx)
        self.run.soon(other_rule.async_check_context)
        sleep(0.1)


TestContext()
