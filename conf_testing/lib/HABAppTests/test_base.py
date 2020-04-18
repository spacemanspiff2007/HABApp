import logging
import threading
import traceback

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


class TestBaseRule(HABApp.Rule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.__tests_funcs = {}

        self.prev_rule: str = None
        self.next_rule: str = None
        self.tests_done = False

        self.__rule_count = 0

        # we have to chain the rules later, because we register the rules only once we loaded successfully.
        self.run_in(2, self._wait_for_rules)
        
        self.register_on_unload(self.do_unload)

    def do_unload(self):
        with LOCK:
            next = self.get_rule(self.next_rule) if self.next_rule is not None else None
            prev = self.get_rule(self.prev_rule) if self.next_rule is not None else None
            if next is not None and prev is not None:
                prev.next_rule = next.rule_name
                next.prev_rule = prev.rule_name
            elif next is None and prev is not None:
                prev.next_rule = None
            elif next is not None and prev is None:
                next.prev_rule = None

    def _wait_for_rules(self):
        with LOCK:
            rules = self.get_rule(None)
            
            # wait until the rule count is constant
            found = len(rules)
            if self.__rule_count != found:
                self.__rule_count = found
                self.run_in(1, self._wait_for_rules)
                return None

            if self.next_rule is not None:
                self.run_in(2, self.start_test_execution)
                return None

            for rule in rules:
                if not isinstance(rule, TestBaseRule):
                    continue
                if rule is self or rule.tests_done:
                    continue

                if rule.next_rule is None:
                    rule.next_rule = self.rule_name
                    self.prev_rule = rule.rule_name
                    return None

            self.run_in(1, self.start_test_execution)

    def start_test_execution(self):
        with LOCK:
            if self.prev_rule is not None:
                return None
        
        self.run_tests(TestResult())

    def add_test(self, name, func, *args, **kwargs):
        assert name not in self.__tests_funcs, name
        self.__tests_funcs[name] = (func, args, kwargs)

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def run_tests(self, result: TestResult):
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

        # run next rule
        self.tests_done = True
        if self.next_rule is not None:
            self.run_soon(self.get_rule(self.next_rule).run_tests, result)
        else:
            log.info( str(result)) if not result.nio else log.error(str(result))
