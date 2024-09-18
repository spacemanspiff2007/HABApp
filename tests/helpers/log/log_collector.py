import logging
from collections.abc import Callable, Iterable
from operator import eq as eq_func
from operator import ge as ge_func
from typing import Any, Final

import pytest
from pytest import LogCaptureFixture
from typing_extensions import Self

from .log_matcher import LogEntryMatcherBase, create_matcher
from .log_utils import SimpleLogRecord


ALL_PYTEST_PHASES = ('setup', 'call', 'teardown')


class LogCollector:
    def __init__(self, caplog: LogCaptureFixture, level: int = logging.WARNING):
        self.caplog: Final = caplog

        self.level_nr: int = level
        self.level_op: Callable[[Any, Any], bool] = ge_func

        self.phases: Iterable[str] = ALL_PYTEST_PHASES

        self.rec_expected: list[LogEntryMatcherBase] = []
        self.rec_ignored: list[LogEntryMatcherBase] = []

        # results
        self.res_records: list[SimpleLogRecord] = []
        self.res_indent: dict[str, int] = {}

    def is_expected_record(self, rec: SimpleLogRecord) -> bool:
        for expected in self.rec_expected:
            if expected.matches(rec):
                return True
        return False

    def is_ignored_record(self, rec: SimpleLogRecord) -> bool:
        for ignored in self.rec_ignored:
            if ignored.matches(rec):
                return True
        return False

    def copy(self) -> Self:
        o = self.__class__(caplog=self.caplog)

        o.level_nr = self.level_nr
        o.level_op = self.level_op

        o.phases = self.phases

        o.expected = self.rec_expected.copy()
        o.ignored = self.rec_ignored.copy()
        return o

    def set_min_level(self, level: int) -> Self:
        self.level_nr = level
        self.level_op = ge_func
        return self

    def set_exact_level(self, level: int) -> Self:
        self.level_nr = level
        self.level_op = eq_func
        return self

    def set_phases(self, *phases: str) -> Self:
        self.phases = tuple(phases)
        return self

    def add_expected(self,
                     name: Iterable[str] | str | None,
                     level: Iterable[str | int] | str | int,
                     msg: Iterable[str] | str):
        self.rec_expected.extend(create_matcher(name, level, msg))

    def add_ignored(self,
                    name: Iterable[str] | str | None,
                    level: Iterable[str | int] | str | int,
                    msg: Iterable[str] | str):
        self.rec_ignored.extend(create_matcher(name, level, msg))

    def update(self) -> Self:
        self.res_records.clear()
        self.res_indent.clear()

        for phase in self.phases:
            if phase not in ALL_PYTEST_PHASES:
                raise ValueError(f'Unknown pytest phase: {phase}')

            prev_rec = None
            for record in self.caplog.get_records(phase):
                if not self.level_op(record.levelno, self.level_nr):
                    continue

                record = SimpleLogRecord.from_rec(record, prev_rec)
                if self.is_ignored_record(record):
                    record.unlink()
                    continue

                # emit warning only on dev machine until we fix asyncio handling
                # TODO: remove this once we fixed asyncio handling
                import os
                if os.name != 'nt' and record.name == 'asyncio':
                    record.unlink()
                    continue

                self.res_records.append(record)
                prev_rec = record
                for n in ('name', 'levelname'):
                    self.res_indent[n] = max(len(getattr(record.rec, n)), self.res_indent.get(n, 0))

        return self

    def get_messages(self) -> list[str]:
        return [
            f'{"ok " if self.is_expected_record(rec) else "   " }'
            f'[{rec.name:>{self.res_indent["name"]:d}s}] | '
            f'{rec.rec.levelname:{self.res_indent["levelname"]:d}s} | '
            f'{rec.rec.getMessage()}'
            for rec in self.res_records
        ]

    def assert_ok(self):
        self.update()

        missing = []
        for expected_msg in self.rec_expected:
            if not expected_msg.found(self.res_records):
                missing.append(expected_msg)

        if missing:
            msg = f'Expected message{"s" if missing != 1 else ""} not found in log:'
            msg += '\n - ' + '\n - '.join(map(str, missing))
            msg += '\nLog:\n' + '\n'.join(self.get_messages())

            pytest.fail(reason=msg)

        for rec in self.res_records:
            if not self.is_expected_record(rec):
                pytest.fail(reason='Error in log:\n' + '\n'.join(self.get_messages()))


def test_cap_warning(test_logs):

    logging.getLogger('TEST').warning('WARNING')

    test_logs.add_expected('TEST', 'WARNING', 'WARNING')
    test_logs.assert_ok()
