import threading
import typing

import HABAppTests

from ._rule_status import TestRuleStatus


LOCK = threading.Lock()


RULE_CTR = 0
TESTS_RULES: typing.Dict[int, 'HABAppTests.TestBaseRule'] = {}


class RuleID:
    def __init__(self, id: int) -> None:
        self.__id = id

    def is_newest(self) -> bool:
        with LOCK:
            if self.__id != RULE_CTR:
                return False
            return True

    def remove(self) -> None:
        pop_test_rule(self.__id)


def get_next_id(rule) -> RuleID:
    global RULE_CTR
    with LOCK:
        RULE_CTR += 1
        TESTS_RULES[RULE_CTR] = rule

        obj = RuleID(RULE_CTR)
    return obj


def pop_test_rule(id: int) -> None:
    with LOCK:
        rule = TESTS_RULES.pop(id)
        rule._rule_status = TestRuleStatus.FINISHED


def get_test_rules() -> typing.Iterable['HABAppTests.TestBaseRule']:
    ret = []
    for k, rule in sorted(TESTS_RULES.items()):
        assert isinstance(rule, HABAppTests.TestBaseRule)
        if rule._rule_status is not TestRuleStatus.CREATED:
            continue
        ret.append(rule)

    return tuple(ret)


def test_rules_running() -> bool:
    for rule in TESTS_RULES.values():
        status = rule._rule_status
        if status is not TestRuleStatus.CREATED and status is not TestRuleStatus.FINISHED:
            return True
    return False
