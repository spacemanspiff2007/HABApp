from unittest.mock import MagicMock

from HABApp import Rule
from tests.helpers import TestEventBus
from ..rule_runner import SimpleRuleRunner


def test_unload_function():

    with SimpleRuleRunner():
        r = Rule()
        m = MagicMock()
        r.on_rule_removed = m
        assert not m.called
    assert m.called


def test_unload_function_exception(eb: TestEventBus):
    eb.allow_errors = True

    with SimpleRuleRunner():
        r = Rule()
        m = MagicMock(side_effect=ValueError)
        r.on_rule_removed = m
        assert not m.called

    assert m.called
