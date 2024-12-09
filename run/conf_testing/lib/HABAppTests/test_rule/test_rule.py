import logging
from collections.abc import Callable, Coroutine
from enum import Enum, auto
from typing import Any, Self, overload

import HABApp
from HABAppTests.test_rule.test_case import TestCase, TestResult, run_test_cases


class TestRuleStatus(Enum):
    CREATED = auto()
    PENDING = auto()
    RUNNING = auto()
    FINISHED = auto()


log = logging.getLogger('HABApp.Tests')


class TestConfig:
    def __init__(self) -> None:
        self.skip_on_failure = False
        self.warning_is_error = False


class TestBaseRule(HABApp.Rule):
    def __init__(self) -> None:
        super().__init__()

        self.config = TestConfig()
        self._rule_status = TestRuleStatus.CREATED
        self._test_cases: dict[str, TestCase] = {}

    @overload
    def set_up(self) -> None: ...

    @overload
    async def set_up(self) -> None: ...

    def set_up(self) -> None:
        pass

    @overload
    def tear_down(self) -> None: ...

    @overload
    async def tear_down(self) -> None: ...

    def tear_down(self) -> None:
        pass

    def add_test(self, name: str, func: Callable | Callable[[...], Coroutine], *args: Any,
                 setup_up: Callable | Callable[[...], Coroutine] | None = None,
                 tear_down: Callable | Callable[[...], Coroutine] | None = None,
                 **kwargs: Any) -> Self:

        tc = TestCase(name, func, args, kwargs, setup_up, tear_down)
        assert tc.name not in self._test_cases
        self._test_cases[tc.name] = tc
        return self

    async def run_test_cases(self) -> list[TestResult]:
        self._rule_status = TestRuleStatus.RUNNING

        results: list[TestResult] = []

        # setup
        tc = TestCase('set_up', self.set_up)
        tr = TestResult(self.__class__.__name__, tc.name)
        await tc.run(tr)
        if tr.state is not tr.state.PASSED:
            results.append(tr)

        results.extend(
            await run_test_cases(
                tuple(self._test_cases.values()), self.__class__.__name__, self,
                skip_on_failure=self.config.skip_on_failure
            )
        )

        # tear down
        tc = TestCase('tear_down', self.tear_down)
        tr = TestResult(self.__class__.__name__, tc.name)
        await tc.run(tr)
        if tr.state is not tr.state.PASSED:
            results.append(tr)

        self._rule_status = TestRuleStatus.FINISHED
        return results
