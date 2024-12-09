from HABApp import Rule
from HABApp.core.asyncio import (
    create_task,
    create_task_from_async,
    run_coro_from_thread,
    run_func_from_async,
    thread_context,
)
from HABApp.core.items import Item


def check_in_thread() -> None:
    if thread_context.get() is None:
        msg = 'Thread context not set!'
        raise ValueError(msg)


def check_in_task() -> None:
    if thread_context.get(None) is not None:
        msg = 'Thread context set!'
        raise ValueError(msg)


class TestThreadPool(Rule):
    """This rule is testing the Scheduler implementation"""

    def __init__(self) -> None:
        super().__init__()

        self.run.soon(self.sync_func_task)
        self.run.soon(self.async_func)

        self.run.soon(self.test_sync_calls)
        self.run.soon(self.test_async_calls)

    def sync_func_task(self) -> int:
        check_in_thread()
        return 7

    def sync_func_async(self) -> int:
        check_in_task()
        return 7

    async def async_func(self) -> int:
        check_in_task()
        return 7

    def test_sync_calls(self) -> None:
        check_in_thread()

        f = create_task(self.async_func())
        assert f.result() == 7

        f = run_func_from_async(self.sync_func_async)
        assert f == 7

        f = run_coro_from_thread(self.async_func(), self.async_func)
        assert f == 7

    async def test_async_calls(self) -> None:
        check_in_task()

        f = create_task(self.async_func())
        assert await f == 7

        f = run_func_from_async(self.sync_func_async)
        assert f == 7

        f = await create_task_from_async(self.async_func())
        assert f == 7


TestThreadPool()


item = Item.get_create_item('RuleLifecycleMethods', initial_value=[])


class TestRuleLifecycleThread(Rule):

    def on_rule_loaded(self) -> None:
        check_in_thread()
        item.value.append('on_rule_loaded_thread')

    def on_rule_removed(self) -> None:
        check_in_thread()
        item.value.append('on_rule_removed_thread')


TestRuleLifecycleThread()


class TestRuleLifecycleTask(Rule):

    async def on_rule_loaded(self) -> None:
        check_in_task()
        item.value.append('on_rule_loaded_task')

    async def on_rule_removed(self) -> None:
        check_in_task()
        item.value.append('on_rule_removed_task')


TestRuleLifecycleTask()
