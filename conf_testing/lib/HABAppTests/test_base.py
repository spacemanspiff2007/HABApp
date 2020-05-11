import logging
import threading
import traceback
import typing

import HABApp

log = logging.getLogger('HABApp.Tests')

LOCK = threading.Lock()


class TestResult:
    def __init__(self):
        self.run = 0
        self.io = 0
        self.nio = 0

    def __repr__(self):
        return f'Processed {self.run:d} Tests: IO: {self.io} NIO: {self.nio}'


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
            rule.run_tests(result)

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
            for line in traceback.format_exc().splitlines():
                log.error(line)
            result.nio += 1
            return None

        test_count = len(self.__tests_funcs)
        log.info(f'Running {test_count} tests for {self.rule_name}')

        width = test_count // 10 + 1
        test_current = 0
        for name, test_data in self.__tests_funcs.items():
            test_current += 1
            result.run += 1

            try:
                func = test_data[0]
                args = test_data[1]
                kwargs = test_data[2]

                msg = func(*args, **kwargs)
                if msg is True or msg is None:
                    msg = ''
            except Exception as e:
                log.error(f'Test "{name}" failed: {e}')
                for line in traceback.format_exc().splitlines():
                    log.error(line)
                result.nio += 1
                continue

            if msg == '':
                result.io += 1
                log.info( f'Test {test_current:{width}}/{test_count} "{name}" successful!')
            else:
                result.nio += 1
                if isinstance(msg, bool):
                    log.error(f'Test {test_current:{width}}/{test_count} "{name}" failed')
                else:
                    log.error(f'Test {test_current:{width}}/{test_count} "{name}" failed: {msg} ({type(msg)})')

        # TEAR DOWN
        try:
            self.tear_down()
        except Exception as e:
            log.error(f'"Set up of {self.__class__.__name__}" failed: {e}')
            for line in traceback.format_exc().splitlines():
                log.error(line)
            result.nio += 1
