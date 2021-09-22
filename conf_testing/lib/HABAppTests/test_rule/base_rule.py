import logging
import time
import typing

import HABApp
from HABApp.core.events.habapp_events import HABAppException
from HABAppTests._rest_patcher import RestPatcher
from ._rule_ids import get_test_rules, get_next_id

log = logging.getLogger('HABApp.Tests')


class TestResult:
    def __init__(self):
        self.run = 0
        self.io = 0
        self.nio = 0
        self.skipped = 0

    def __iadd__(self, other):
        assert isinstance(other, TestResult)
        self.run += other.run
        self.io  += other.io
        self.nio += other.nio
        self.skipped += other.skipped
        return self

    def __repr__(self):
        return f'Processed {self.run:d} Tests: IO: {self.io} NIO: {self.nio} skipped: {self.skipped}'


class TestConfig:
    def __init__(self):
        self.skip_on_failure = False
        self.warning_is_error = False


class TestBaseRule(HABApp.Rule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.__tests_funcs = {}
        self.tests_started = False

        self._rule_id = get_next_id(self)

        self.config = TestConfig()

        # we have to chain the rules later, because we register the rules only once we loaded successfully.
        self.run.at(2, self.__execute_run)

        # collect warnings and infos
        self.listen_event(HABApp.core.const.topics.WARNINGS, self.__warning)
        self.listen_event(HABApp.core.const.topics.ERRORS, self.__error)
        self.__warnings = 0
        self.__errors = 0

    def __warning(self, event: str):
        self.__warnings += 1
        for line in event.splitlines():
            log.warning(line)

    def __error(self, event):
        self.__errors += 1
        msg = event.to_str() if isinstance(event, HABAppException) else event
        for line in msg.splitlines():
            log.error(line)

    def __execute_run(self):
        if not self._rule_id.is_newest():
            return None

        result = TestResult()
        for rule in get_test_rules():
            r = TestResult()
            rule.run_tests(r)
            result += r

        log.info('-' * 120)
        log.info(str(result)) if not result.nio else log.error(str(result))
        print('-' * 120)
        print(str(result))
        return None

    def add_test(self, name, func, *args, **kwargs):
        assert name not in self.__tests_funcs, name
        self.__tests_funcs[name] = (func, args, kwargs)

    def set_up(self):
        pass

    def tear_down(self):
        pass

    @staticmethod
    def _run_patched(name, func, *args, **kwargs) -> [bool, typing.Any]:
        time.sleep(0.05)

        msg = None
        error = False

        try:
            with RestPatcher(name):
                msg = func(*args, **kwargs)
        except Exception as e:
            log.error(f'{name} failed: {e}')
            for line in HABApp.core.wrapper.format_exception(e):
                log.error(line)
            error = True
        return error, msg

    def run_tests(self, result: TestResult):
        self.tests_started = True

        c_name = self.__class__.__name__

        # SET UP
        err, _ = self._run_patched(f'{c_name}.set_up', self.set_up)
        if err:
            result.nio += 1
            return None

        # EXECUTE TESTS
        test_count = len(self.__tests_funcs)
        log.info('')
        log.info(f'Running {test_count} tests for {self.rule_name}')

        for name, test_data in self.__tests_funcs.items():
            self.__run_test(name, test_data, result)

        # TEAR DOWN
        err, _ = self._run_patched(f'{c_name}.tear_down', self.tear_down)
        if err:
            result.nio += 1
            return None

    def __run_test(self, name: str, data: tuple, result: TestResult):
        test_count = len(self.__tests_funcs)
        width = test_count // 10 + 1

        result.run += 1

        self.__warnings = 0
        self.__errors = 0

        # add possibility to skip on failure
        if self.config.skip_on_failure:
            if result.nio:
                result.skipped += 1
                log.warning(f'Test {result.run:{width}}/{test_count} "{name}" skipped!')
                return None

        func = data[0]
        args = data[1]
        kwargs = data[2]

        err, msg = self._run_patched(self.__class__.__name__ + '.' + name, func, *args, **kwargs)
        if err:
            result.nio += 1
            return None

        if msg is True or msg is None:
            msg = ''

        if self.__errors:
            msg = f'{", " if msg else ""}{self.__errors} error{"s" if self.__errors != 1 else ""} in worker'
        if self.config.warning_is_error and self.__warnings:
            msg = f'{", " if msg else ""}{self.__errors} warning{"s" if self.__errors != 1 else ""} in worker'

        if msg == '':
            result.io += 1
            log.info(f'Test {result.run:{width}}/{test_count} "{name}" successful!')
        elif isinstance(msg, str) and msg.lower() == 'SKIP':
            result.skipped += 1
            log.info(f'Test {result.run:{width}}/{test_count} "{name}" skipped!')
        else:
            result.nio += 1
            if isinstance(msg, bool):
                log.error(f'Test {result.run:{width}}/{test_count} "{name}" failed')
            else:
                log.error(f'Test {result.run:{width}}/{test_count} "{name}" failed: {msg} ({type(msg)})')
