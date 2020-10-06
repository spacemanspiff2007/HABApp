import logging
import threading
import typing

import HABApp
from ._rest_patcher import RestPatcher

log = logging.getLogger('HABApp.Tests')

LOCK = threading.Lock()


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


RULE_CTR = 0
TESTS_RULES: typing.Dict[int, 'TestBaseRule'] = {}


def get_next_id(rule):
    global RULE_CTR
    with LOCK:
        RULE_CTR += 1
        TESTS_RULES[RULE_CTR] = rule
        return RULE_CTR


def pop_rule(rule_id: int):
    with LOCK:
        TESTS_RULES.pop(rule_id)


class TestBaseRule(HABApp.Rule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.__tests_funcs = {}
        self.tests_started = False

        self.__id = get_next_id(self)
        self.register_on_unload(lambda: pop_rule(self.__id))

        self.config = TestConfig()

        # we have to chain the rules later, because we register the rules only once we loaded successfully.
        self.run_in(2, self.__execute_run)

    def __execute_run(self):
        with LOCK:
            if self.__id != RULE_CTR:
                return None

        result = TestResult()
        for k, rule in sorted(TESTS_RULES.items()):
            assert isinstance(rule, TestBaseRule)
            if rule.tests_started:
                continue
            r = TestResult()
            rule.run_tests(r)
            result += r

        log.info('-' * 120)
        log.info(str(result)) if not result.nio else log.error(str(result))
        print(str(result))
        return None

    def add_test(self, name, func, *args, **kwargs):
        assert name not in self.__tests_funcs, name
        self.__tests_funcs[name] = (func, args, kwargs)

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def run_tests(self, result: TestResult):
        self.tests_started = True

        try:
            self.set_up()
        except Exception as e:
            log.error(f'"Set up of {self.__class__.__name__}" failed: {e}')
            for line in HABApp.core.wrapper.format_exception(e):
                log.error(line)
            result.nio += 1
            return None

        test_count = len(self.__tests_funcs)
        log.info(f'Running {test_count} tests for {self.rule_name}')

        for name, test_data in self.__tests_funcs.items():
            self.__run_test(name, test_data, result)

        # TEAR DOWN
        try:
            self.tear_down()
        except Exception as e:
            log.error(f'"Set up of {self.__class__.__name__}" failed: {e}')
            for line in HABApp.core.wrapper.format_exception(e):
                log.error(line)
            result.nio += 1

    def __run_test(self, name: str, data: tuple, result: TestResult):
        test_count = len(self.__tests_funcs)
        width = test_count // 10 + 1

        result.run += 1

        # add possibility to skip on failure
        if self.config.skip_on_failure:
            if result.nio:
                result.skipped += 1
                log.warning(f'Test {result.run:{width}}/{test_count} "{name}" skipped!')
                return None

        try:
            func = data[0]
            args = data[1]
            kwargs = data[2]
            with RestPatcher(self.__class__.__name__ + '.' + name):
                msg = func(*args, **kwargs)
        except Exception as e:
            log.error(f'Test "{name}" failed: {e}')
            for line in HABApp.core.wrapper.format_exception(e):
                log.error(line)
            result.nio += 1
            return None

        if msg is True or msg is None:
            msg = ''
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
