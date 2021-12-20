from unittest.mock import MagicMock

from HABApp import Rule
from ..rule_runner import SimpleRuleRunner


def test_unload_function():

    with SimpleRuleRunner():
        r = Rule()
        m = MagicMock()
        r.on_rule_unload = m
        assert not m.called
    assert m.called


def test_unload_function_exception():

    with SimpleRuleRunner():
        r = Rule()
        m = MagicMock(side_effect=ValueError)
        r.on_rule_unload = m
        assert not m.called
    assert m.called
