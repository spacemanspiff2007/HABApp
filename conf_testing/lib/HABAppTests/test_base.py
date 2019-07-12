import logging
import threading
import traceback

import HABApp

log = logging.getLogger('HABApp.Tests')

LOCK = threading.Lock()


class TestBaseRule(HABApp.Rule):
    """This rule is testing the OpenHAB data types by posting values and checking the events"""

    def __init__(self):
        super().__init__()

        self.__tests_funcs = {}

        self.prev_rule: str = None
        self.next_rule: str = None
        self.tests_done = False

        with LOCK:
            # if we have only one rule it's not a list
            rules = self.get_rule(None)
            if isinstance(rules, HABApp.Rule):
                rules = [rules]

            for rule in rules:
                if not isinstance(rule, TestBaseRule):
                    continue
                if rule is self or rule.tests_done:
                    continue

                if rule.next_rule is None:
                    rule.next_rule = self.rule_name
                    self.prev_rule = rule.rule_name
                    break

        self.run_in(2, self.start_test_execution)

    def start_test_execution(self):
        if self.prev_rule is not None:
            return None

        self.run_tests()


    def add_test(self, name, func, *args, **kwargs):
        assert name not in self.__tests_funcs
        self.__tests_funcs[name] = (func, args, kwargs)

    def run_tests(self):
        for name, test_data in self.__tests_funcs.items():

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
                continue

            if msg == '':
                log.info( f'Test "{name}" successful!')
            else:
                if isinstance(msg, bool):
                    log.error(f'Test "{name}" failed')
                else:
                    log.error(f'Test "{name}" failed: {msg} ({type(msg)})')

        # run next rule
        self.tests_done = False
        if self.next_rule is not None:
            self.run_soon(self.get_rule(self.next_rule).run_tests)
