import logging
from enum import IntEnum, auto
from typing import List, Optional

import HABApp
from HABAppTests.errors import TestCaseFailed, TestCaseWarning

log = logging.getLogger('HABApp.Tests')


class TestResultStatus(IntEnum):
    NOT_SET = auto()

    SKIPPED = auto()
    PASSED = auto()

    WARNING = auto()

    FAILED = auto()
    ERROR = auto()


assert TestResultStatus.NOT_SET < TestResultStatus.SKIPPED
assert TestResultStatus.SKIPPED < TestResultStatus.PASSED
assert TestResultStatus.PASSED < TestResultStatus.WARNING
assert TestResultStatus.WARNING < TestResultStatus.FAILED
assert TestResultStatus.FAILED < TestResultStatus.ERROR


class TestResult:
    def __init__(self, cls_name: str, test_name: str, test_nr: str = ''):
        self.cls_name = cls_name
        self.test_name = test_name
        self.test_nr = test_nr

        self.state = TestResultStatus.NOT_SET
        self.msgs: List[str] = []

    def is_set(self):
        return self.state != TestResultStatus.NOT_SET

    def set_state(self, new_state: TestResultStatus):
        if self.state <= new_state:
            self.state = new_state

    def exception(self, e: Exception):
        if isinstance(e, TestCaseFailed):
            self.set_state(TestResultStatus.FAILED)
            self.add_msg(e.msg)
            return None
        if isinstance(e, TestCaseWarning):
            self.set_state(TestResultStatus.WARNING)
            self.add_msg(e.msg)
            return None

        self.add_msg(f'Exception: {e}')
        self.state = TestResultStatus.ERROR

        for line in HABApp.core.wrapper.format_exception(e):
            log.error(line)

    def add_msg(self, msg: str):
        self.msgs.append(msg)

    def log(self, name: Optional[str] = None):
        if name is None:
            name = f'{self.cls_name}.{self.test_name}'
        nr = f' {self.test_nr} ' if self.test_nr else ' '
        msg = ': ' + ", ".join(self.msgs) if self.msgs else ''

        prefix = f'{nr}"{name}"'

        if self.state is TestResultStatus.PASSED:
            return log.info(f'{prefix} successful')
        if self.state is TestResultStatus.SKIPPED:
            return log.info(f'{prefix} skipped')
        if self.state is TestResultStatus.WARNING:
            return log.warning(f'{prefix} warning{msg}')
        if self.state is TestResultStatus.FAILED:
            return log.error(f'{prefix} failed{msg}')
        if self.state is TestResultStatus.ERROR:
            return log.error(f'{prefix} error{msg}')
