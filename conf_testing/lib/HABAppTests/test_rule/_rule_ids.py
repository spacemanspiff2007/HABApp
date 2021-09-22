import threading
import typing

import HABAppTests

LOCK = threading.Lock()


RULE_CTR = 0
TESTS_RULES: typing.Dict[int, 'HABAppTests.TestBaseRule'] = {}


class RuleID:
    def __init__(self, id: int):
        self.__id = id

    def is_newest(self) -> bool:
        with LOCK:
            if self.__id != RULE_CTR:
                return False
            return True

    def remove(self):
        pop_test_rule(self.__id)


def get_next_id(rule) -> RuleID:
    global RULE_CTR
    with LOCK:
        RULE_CTR += 1
        TESTS_RULES[RULE_CTR] = rule

        obj = RuleID(RULE_CTR)

    rule.register_on_unload(obj.remove)
    return obj


def pop_test_rule(id: int):
    with LOCK:
        TESTS_RULES.pop(id)


def get_test_rules() -> typing.Iterable['HABAppTests.TestBaseRule']:
    ret = []
    for k, rule in sorted(TESTS_RULES.items()):
        assert isinstance(rule, HABAppTests.TestBaseRule)
        if rule.tests_started:
            continue
        ret.append(rule)

    return ret
