import logging
from typing import Dict
from typing import List

import HABApp
from HABAppTests.test_rule.test_case import TestResult, TestResultStatus, TestCase
from ._rule_ids import get_test_rules, get_next_id, test_rules_running
from ._rule_status import TestRuleStatus

log = logging.getLogger('HABApp.Tests')


class TestConfig:
    def __init__(self):
        self.skip_on_failure = False
        self.warning_is_error = False


class TestBaseRule(HABApp.Rule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()
        self._rule_status = TestRuleStatus.CREATED
        self._rule_id = get_next_id(self)
        self._tests: Dict[str, TestCase] = {}

        self.__warnings = []
        self.__errors = []
        self.__sub_warning = None
        self.__sub_errors = None

        self.config = TestConfig()

        self.__worst_result = TestResultStatus.PASSED

        # we have to chain the rules later, because we register the rules only once we loaded successfully.
        self.run.at(2, self.__execute_run)

    def on_rule_unload(self):
        self._rule_id.remove()

    # ------------------------------------------------------------------------------------------------------------------
    # Overrides and test
    def set_up(self):
        pass

    def tear_down(self):
        pass

    def add_test(self, name, func: callable, *args, **kwargs):
        tc = TestCase(name, func, args, kwargs)
        assert tc.name not in self._tests
        self._tests[tc.name] = tc

    # ------------------------------------------------------------------------------------------------------------------
    # Rule execution
    def __execute_run(self):
        if not self._rule_id.is_newest():
            return None

        # If we currently run a test wait until it is complete
        if test_rules_running():
            self.run.at(2, self.__execute_run)
            return None

        ergs = []
        rules = get_test_rules()
        for rule in rules:
            # mark rules for execution
            rule._rule_status = TestRuleStatus.PENDING
        for rule in rules:
            # It's possible that we unload a rule before it was run
            if rule._rule_status is not TestRuleStatus.PENDING:
                continue
            ergs.extend(rule._run_tests())

        skipped = tuple(filter(lambda x: x.state is TestResultStatus.SKIPPED, ergs))
        passed  = tuple(filter(lambda x: x.state is TestResultStatus.PASSED, ergs))
        warning = tuple(filter(lambda x: x.state is TestResultStatus.WARNING, ergs))
        failed  = tuple(filter(lambda x: x.state is TestResultStatus.FAILED, ergs))
        error   = tuple(filter(lambda x: x.state is TestResultStatus.ERROR, ergs))

        def plog(msg: str):
            print(msg)
            log.info(msg)

        parts = [f'{len(ergs)} executed', f'{len(passed)} passed']
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

    # ------------------------------------------------------------------------------------------------------------------
    # Event from the worker
    def __event_warning(self, event):
        self.__warnings.append(event)

    def __event_error(self, event):
        self.__errors.append(event)

    def _worker_events_sub(self):
        assert self.__sub_warning is None
        assert self.__sub_errors is None
        self.__sub_warning = self.listen_event(HABApp.core.const.topics.TOPIC_WARNINGS, self.__event_warning)
        self.__sub_errors = self.listen_event(HABApp.core.const.topics.TOPIC_ERRORS, self.__event_error)

    def _worker_events_cancel(self):
        if self.__sub_warning is not None:
            self.__sub_warning.cancel()
        if self.__sub_errors is not None:
            self.__sub_errors.cancel()

    # ------------------------------------------------------------------------------------------------------------------
    # Test execution
    def __exec_tc(self, res: TestResult, tc: TestCase):
        self.__warnings.clear()
        self.__errors.clear()

        tc.run(res)

        if self.__warnings:
            res.set_state(TestResultStatus.WARNING)
            ct = len(self.__warnings)
            msg = f'{ct} warning{"s" if ct != 1 else ""} in worker'
            res.add_msg(msg)
            self.__warnings.clear()

        if self.__errors:
            res.set_state(TestResultStatus.ERROR)
            ct = len(self.__errors)
            msg = f'{ct} error{"s" if ct != 1 else ""} in worker'
            res.add_msg(msg)
            self.__errors.clear()

        self.__worst_result = max(self.__worst_result, res.state)

    def _run_tests(self) -> List[TestResult]:
        self._rule_status = TestRuleStatus.RUNNING
        self._worker_events_sub()

        results = []

        # setup
        tc = TestCase('set_up', self.set_up)
        tr = TestResult(self.__class__.__name__, tc.name)
        self.__exec_tc(tr, tc)
        if tr.state is not tr.state.PASSED:
            results.append(tr)

        results.extend(self.__run_tests())

        # tear down
        tc = TestCase('tear_down', self.set_up)
        tr = TestResult(self.__class__.__name__, tc.name)
        self.__exec_tc(tr, tc)
        if tr.state is not tr.state.PASSED:
            results.append(tr)

        self._worker_events_cancel()
        self._rule_status = TestRuleStatus.FINISHED
        return results

    def __run_tests(self) -> List[TestResult]:
        count = len(self._tests)
        width = 1
        while count >= 10 ** width:
            width += 1

        c_name = self.__class__.__name__
        results = [
            TestResult(c_name, tc.name, f'{i + 1:{width}d}/{count}') for i, tc in enumerate(self._tests.values())
        ]

        log.info('')
        log.info(f'Running {count} tests for {c_name}')

        for res, tc in zip(results, self._tests.values()):
            if self.config.skip_on_failure and self.__worst_result >= TestResultStatus.FAILED:
                res.set_state(TestResultStatus.SKIPPED)
                res.log()
                continue

            self.__exec_tc(res, tc)
            res.log()

        return results
