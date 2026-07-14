import asyncio

import pytest

from HABApp import Rule
from HABApp.testing import UserTimeControl
from HABApp.testing.conftest import *  # noqa: F403
from HABApp.testing.executor import TestingExecutorFactory


class SyncErrorRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        self.run.soon(self.error_func)

    def error_func(self) -> None:
        1 / 0


class AsyncErrorRule(Rule):
    def __init__(self) -> None:
        super().__init__()
        self.run.soon(self.error_func)

    async def error_func(self) -> None:
        1 / 0


@pytest.mark.ignore_log_errors
async def test_error_sync(
        capsys, time_control: UserTimeControl, rule_hook, testing_executor_factory: TestingExecutorFactory) -> None:

    SyncErrorRule()

    e, = testing_executor_factory.errors
    assert isinstance(e, ZeroDivisionError)
    testing_executor_factory.errors.clear()


@pytest.mark.ignore_log_errors
async def test_error_async(
        capsys, time_control: UserTimeControl, rule_hook, testing_executor_factory: TestingExecutorFactory) -> None:

    AsyncErrorRule()

    await asyncio.sleep(0)

    e, = testing_executor_factory.errors
    assert isinstance(e, ZeroDivisionError)
    testing_executor_factory.errors.clear()
