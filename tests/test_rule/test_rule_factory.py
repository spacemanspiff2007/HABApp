import pytest

from HABApp.rule import Rule, create_rule
from tests import SimpleRuleRunner


def test_rule_no_create():
    class MyRule(Rule):
        pass

    assert create_rule(MyRule) is None


@pytest.mark.no_internals()
def test_rule_create():
    class MyRule(Rule):
        pass

    with SimpleRuleRunner():
        r = create_rule(MyRule)

    assert isinstance(r, MyRule)
