import logging
from collections.abc import Callable, Coroutine
from enum import Enum, auto
from typing import Any, overload, Self

import HABApp
from HABAppTests.test_rule.test_case import TestCase, TestResult, TestResultStatus
from HABAppTests.utils import get_file_path_of_obj


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
    def set_up(self): ...

    @overload
    async def set_up(self): ...

    def set_up(self):
        pass

    @overload
    def tear_down(self): ...

    @overload
    async def tear_down(self): ...

    def tear_down(self):
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

        results.extend(await self._run_rule_tests())

        # tear down
        tc = TestCase('tear_down', self.tear_down)
        tr = TestResult(self.__class__.__name__, tc.name)
        await tc.run(tr)
        if tr.state is not tr.state.PASSED:
            results.append(tr)

        self._rule_status = TestRuleStatus.FINISHED
        return results

    async def _run_rule_tests(self) -> list[TestResult]:
        count = len(self._test_cases)
        width = len(str(count))

        c_name = self.__class__.__name__
        results = [
            TestResult(c_name, tc.name, f'{i:{width}d}/{count}') for i, tc in enumerate(self._test_cases.values(), 1)
        ]

        log.info('')
        log.info(
            f'Running {count:d} test{"s" if count != 1 else ""} for {c_name:s}  (from "{get_file_path_of_obj(self)}")'
        )

        for res, tc in zip(results, self._test_cases.values(), strict=True):
            if self.config.skip_on_failure and max(r.state for r in results) >= TestResultStatus.FAILED:
                res.set_state(TestResultStatus.SKIPPED)
                res.log()
                continue

            await tc.run(res)
            res.log()

        return results
