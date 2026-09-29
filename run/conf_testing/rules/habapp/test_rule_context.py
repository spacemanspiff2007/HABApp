import threading
from time import sleep

from HABAppTests import TestBaseRule

from HABApp import Rule
from HABApp.core.errors import ContextNotFoundError
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
        self.add_test('TestUserThreadContext', self.test_user_thread_context)
        self.add_test('TestUserThreadRuleContext', self.test_user_thread_rule_context)

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

    def test_user_thread_context(self) -> None:

        objs = []

        def thread_func() -> None:
            try:
                cxt = get_current_context()
            except Exception as e:
                ctx = e

            objs.append(ctx)

        t = threading.Thread(target=thread_func)
        t.start()
        t.join()

        # The context should not leak into the thread
        assert len(objs) == 1
        assert isinstance(objs[0], ContextNotFoundError)

    def test_user_thread_rule_context(self) -> None:

        # user calls rule from a thread - should work as expected
        t = threading.Thread(target=self.test_get_context)
        t.start()
        t.join()


TestContext()
