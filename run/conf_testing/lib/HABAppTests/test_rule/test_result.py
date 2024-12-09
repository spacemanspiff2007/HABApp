import logging
from enum import IntEnum, auto
from typing import Final

import HABApp
from HABAppTests.errors import TestCaseFailed


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
    def __init__(self, cls_name: str, test_name: str, test_nr: str = '') -> None:
        self.group_name: Final = cls_name
        self.test_name: Final = test_name
        self.test_nr: Final = test_nr

        self.state = TestResultStatus.NOT_SET
        self.msgs: Final[list[str]] = []

    def set_state(self, new_state: TestResultStatus) -> None:
        if self.state <= new_state:
            self.state = new_state

    def exception(self, e: Exception) -> None:
        if isinstance(e, TestCaseFailed):
            self.set_state(TestResultStatus.FAILED)
            self.add_msg(e.msg)
            return None

        # if isinstance(e, AssertionError):
        #     self.set_state(TestResultStatus.FAILED)
        #     self.add_msg(f'{e}')
        #     self.add_msg(f'  {e.args}')
        #     return None

        self.add_msg(f'Exception: {e}')
        self.state = TestResultStatus.ERROR

        for line in HABApp.core.wrapper.format_exception(e):
            log.error(line)

    def add_msg(self, msg: str) -> None:
        for line in msg.splitlines():
            self.msgs.append(line)

    def log(self, name: str | None = None) -> None:
        if name is None:
            name = f'{self.group_name}.{self.test_name}'
        nr = f' {self.test_nr} ' if self.test_nr else ' '
        prefix = f'{nr}"{name}"'

        if self.state is TestResultStatus.PASSED:
            return log.info(f'{prefix} successful')
        if self.state is TestResultStatus.SKIPPED:
            return log.warning(f'{prefix} skipped')

        log_func = log.error
        if self.state is TestResultStatus.WARNING:
            log_func = log.warning

        first_msg = self.msgs[0] if self.msgs else ''

        log_func(f'{prefix} {self.state.name.lower()}: {first_msg}')
        for msg in self.msgs[1:]:
            log_func(f'{"":8s}{msg}')
        return None
