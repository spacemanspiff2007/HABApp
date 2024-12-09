import logging

import HABApp
from HABApp.core import shutdown
from HABApp.core.const.topics import TOPIC_FILES
from HABApp.core.events import EventFilter
from HABApp.core.events.habapp_events import RequestFileLoadEvent
from HABApp.core.lib import SingleTask
from HABApp.core.wrapper import ignore_exception
from HABAppTests.test_rule.test_case import TestResult, TestResultStatus

from .test_rule import TestBaseRule, TestRuleStatus


log = logging.getLogger('HABApp.Tests')


class TestRunnerRule(HABApp.Rule):
    def __init__(self) -> None:
        super().__init__()

        self.listen_event(TOPIC_FILES, self._file_event, EventFilter(event_class=RequestFileLoadEvent))
        self.countdown = self.run.countdown(3, self._files_const)
        self.countdown.reset()

        self.task = SingleTask(self._run_tests)

    async def _file_event(self, event) -> None:
        self.countdown.reset()

    async def _files_const(self) -> None:
        self.task.start_if_not_running()

    def _get_next_rule(self) -> TestBaseRule | None:
        all_rules = [r for r in self.get_rule(None) if isinstance(r, TestBaseRule)]
        for rule in all_rules:
            if rule._rule_status is TestRuleStatus.CREATED:
                rule._rule_status = TestRuleStatus.PENDING
            if rule._rule_status is TestRuleStatus.PENDING:
                return rule
        return None

    @ignore_exception
    async def _run_tests(self) -> None:
        results: list[TestResult] = []

        while (rule := self._get_next_rule()) is not None and not shutdown.is_requested():
            results.extend(await rule.run_test_cases())

        await self.tests_done(results)

        skipped = tuple(x for x in results if x.state is TestResultStatus.SKIPPED)
        passed  = tuple(x for x in results if x.state is TestResultStatus.PASSED)
        warning = tuple(x for x in results if x.state is TestResultStatus.WARNING)
        failed  = tuple(x for x in results if x.state is TestResultStatus.FAILED)
        error   = tuple(x for x in results if x.state is TestResultStatus.ERROR)

        def plog(msg: str) -> None:
            print(msg)
            log.info(msg)

        parts = [f'{len(results)} executed', f'{len(passed)} passed']
        if skipped:
            parts.append(f'{len(skipped)} skipped')
        if warning:
            parts.append(f'{len(warning)} warning{"" if len(warning) == 1 else "s"}')
        parts.append(f'{len(failed)} failed')
        if error:
            parts.append(f'{len(error)} error{"" if len(error) == 1 else "s"}')

        plog('')
        plog('-' * 120)
        plog(', '.join(parts))

    async def tests_done(self, results: list[TestResult]) -> None:
        raise NotImplementedError()
